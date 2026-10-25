package io.mosip.testrig;

import com.aventstack.extentreports.ExtentReports;
import com.aventstack.extentreports.ExtentTest;
import com.aventstack.extentreports.Status;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.testng.Assert;
import org.testng.SkipException;
import org.testng.annotations.*;
import java.io.File;
import java.nio.file.Path;
import java.nio.file.Files;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.TimeUnit;

/**
 * Bridges official conformance outcomes into TestNG with explicit run identity.
 * PASSED and WARNING complete normally; SKIPPED and validated EXPECTED_FAILURE
 * raise SkipException. Other outcomes fail assertions, including REVIEW because
 * evidence awaiting official review cannot establish a passing result.
 * The separate gate assertion also rejects incomplete reporting or runner failure.
 */
public class OpenIDConformanceTest {
    protected static final ObjectMapper mapper = new ObjectMapper();
    protected static ExtentReports extent;
    protected static String reportPath;
    protected static int runnerExitCode;
    protected static JsonNode report;
    protected static boolean initialized;
    protected String targetComponent = "combined";

    protected static File resolveSummaryFile() {
        String supplied = System.getProperty("conformance.summary");
        if (supplied != null) return new File(supplied);
        File parent = new File("../reports/conformance-summary.json");
        return parent.exists() ? parent : new File("reports/conformance-summary.json");
    }

    @BeforeSuite(alwaysRun = true)
    @Parameters({"component", "oidfUrl", "targetEndpoint", "certifyUrl", "verifyUrl"})
    public void setupSuite(@Optional("combined") String component,
                           @Optional("https://localhost:8443") String oidfUrl,
                           @Optional("") String targetEndpoint,
                           @Optional("https://host.docker.internal:8446") String certifyUrl,
                           @Optional("https://localhost:8445/v1/verify") String verifyUrl) throws Exception {
        targetComponent = component;
        if (initialized) return;
        initialized = true;
        File summary = resolveSummaryFile().getAbsoluteFile();
        reportPath = new File(summary.getParentFile(), "extent-report.html").getPath();
        extent = ExtentReportManager.getInstance(reportPath);
        if (!Boolean.getBoolean("conformance.consumeReport")) {
            File script = new File("runner/runner.py");
            if (!script.exists()) script = new File("../runner/runner.py");
            script = script.getCanonicalFile();
            List<String> command = new ArrayList<>();
            command.add(System.getProperty("conformance.python", System.getProperty("os.name").toLowerCase().contains("win") ? "python" : "python3"));
            command.add(script.getPath());
            if ("combined".equals(component)) command.add("--combined");
            else { command.add("--component"); command.add(component); }
            String endpoint = System.getProperty("env.endpoint", System.getenv("ENV_ENDPOINT"));
            if (endpoint == null || endpoint.isBlank()) endpoint = targetEndpoint;
            if (endpoint != null && !endpoint.isBlank()) {
                if ("certify".equals(component)) certifyUrl = endpoint;
                if ("verify".equals(component)) verifyUrl = endpoint;
            }
            command.addAll(Arrays.asList("--oidf-url", System.getProperty("oidf.url", oidfUrl),
                "--certify-url", System.getProperty("certify.url", certifyUrl),
                "--verify-url", System.getProperty("verify.url", verifyUrl),
                "--reports-dir", summary.getParent()));
            if (Boolean.getBoolean("conformance.insecure")) command.add("--insecure");
            Process process = new ProcessBuilder(command).directory(script.getParentFile().getParentFile()).inheritIO().start();
            if (!process.waitFor(Long.getLong("conformance.processTimeoutSeconds", 3600L), TimeUnit.SECONDS)) {
                java.util.List<ProcessHandle> children = process.descendants().collect(java.util.stream.Collectors.toList());
                children.forEach(ProcessHandle::destroyForcibly);
                process.destroyForcibly();
                process.waitFor(5, TimeUnit.SECONDS);
                throw new IllegalStateException("Conformance subprocess exceeded timeout");
            }
            runnerExitCode = process.exitValue();
        }
        Assert.assertTrue(summary.isFile(), "Conformance summary missing");
        report = mapper.readTree(summary);
        Assert.assertEquals(report.path("schema_version").asInt(), 2, "Unsupported report schema");
        Assert.assertFalse(report.path("run_id").asText().isEmpty(), "Report run ID missing");
        if (Boolean.getBoolean("conformance.consumeReport")) {
            String expected = System.getProperty("conformance.runId", "");
            Assert.assertFalse(expected.isEmpty(), "Consuming a report requires -Dconformance.runId");
            Assert.assertEquals(report.path("run_id").asText(), expected, "Stale/different report identity");
        }
        Instant timestamp = OffsetDateTime.parse(report.path("consolidated").path("timestamp").asText()).toInstant();
        long age = Instant.now().getEpochSecond() - timestamp.getEpochSecond();
        Assert.assertTrue(age >= -60 && age <= Long.getLong("conformance.maxReportAgeSeconds", 7200L), "Report is stale or future dated");
        if ("combined".equals(component)) {
            Assert.assertTrue(report.path("runs").has("certify") && report.path("runs").has("verify"), "Combined report must contain both components");
        } else Assert.assertTrue(report.path("runs").has(component), "Requested module absent from report");
    }

    @DataProvider(name = "conformanceTestCases")
    public Object[][] provideTestCases() throws Exception {
        List<Object[]> rows = new ArrayList<>();
        JsonNode results = "combined".equals(targetComponent) ? report.path("consolidated").path("results") : report.path("runs").path(targetComponent).path("results");
        results.fields().forEachRemaining(e -> rows.add(new Object[]{e.getKey(), e.getValue().asText()}));
        if (rows.isEmpty()) rows.add(new Object[]{"Missing-Conformance-Results", "ERROR"});
        return rows.toArray(new Object[0][]);
    }

    @Test(dataProvider = "conformanceTestCases")
    public void testConformanceModule(String name, String status) {
        ExtentTest test = extent.createTest(name);
        switch (status) {
            case "PASSED": test.pass("OIDF passed"); break;
            case "WARNING": test.warning("OIDF warning; see raw logs"); break;
            case "SKIPPED":
            case "EXPECTED_FAILURE":
                test.skip(status); throw new SkipException(status + ": " + name);
            default: test.fail(status); Assert.fail(status + ": " + name);
        }
    }

    @Test(priority = 1000)
    public void testReleaseGateBenchmark() {
        ExtentTest test = extent.createTest("Release gate: " + targetComponent);
        try {
        JsonNode gate = "combined".equals(targetComponent) ? report.path("consolidated") : report.path("runs").path(targetComponent).path("summary");
        Assert.assertEquals(runnerExitCode, 0, "Runner process failed");
        Assert.assertTrue(gate.path("combined".equals(targetComponent) ? "gate_met" : "is_gated_pass").asBoolean(false), "Release gate rejected");
        if (!"combined".equals(targetComponent)) {
            Assert.assertTrue(gate.path("regression_gate_met").asBoolean(
                report.path("consolidated").path("gate_met").asBoolean(false)), "Component regression gate rejected");
            if (gate.has("gate_met"))
                Assert.assertTrue(gate.path("gate_met").asBoolean(false), "Effective component gate rejected");
        }
        Assert.assertTrue(gate.path("passed").asInt() > 0, "No passing tests");
        test.pass("Release gate accepted");
        } catch (AssertionError failure) {
            test.fail(failure.getMessage());
            throw failure;
        }
    }

    @AfterSuite(alwaysRun = true)
    public void tearDownSuite() {
        if (extent != null) ExtentReportManager.flush();
    }

    public static void uploadCompletedArtifacts() {
        if (report == null) return;
        String prefix = System.getProperty("conformance.artifactPrefix", "openid-conformance/" + report.path("run_id").asText() + "/");
        File directory = resolveSummaryFile().getAbsoluteFile().getParentFile();
        Set<String> rootFiles = new HashSet<>(Arrays.asList("conformance-summary.json", "combined-conformance-badge.svg", "extent-report.html"));
        Set<String> testIds = new HashSet<>();
        report.path("runs").fields().forEachRemaining(entry -> {
            rootFiles.add(entry.getKey() + "-conformance-report.json");
            rootFiles.add(entry.getKey() + "-conformance-badge.svg");
            rootFiles.add("plan-" + entry.getValue().path("summary").path("plan_id").asText() + "-export.zip");
            entry.getValue().path("modules").forEach(module -> {
                String id = module.path("test_id").asText();
                if (!id.isEmpty()) { testIds.add(id); rootFiles.add(id + "-log.json"); }
            });
        });
        try (java.util.stream.Stream<Path> artifacts = Files.walk(directory.toPath())) {
            artifacts.filter(Files::isRegularFile).forEach(artifact -> {
                Path relative = directory.toPath().relativize(artifact);
                if ((relative.getNameCount() == 1 && rootFiles.contains(relative.toString()))
                    || (relative.getNameCount() > 1 && testIds.contains(relative.getName(0).toString())))
                    MinioArtifactUploader.uploadArtifact(artifact.toString(), prefix + relative.toString().replace('\\', '/'));
            });
        } catch (java.io.IOException failure) { throw new IllegalStateException("Unable to enumerate actual run artifacts", failure); }
        // TestNG generates its XML after @AfterSuite. Upload only after execution/report generation.
        File testng = new File("target/surefire-reports/testng-results.xml");
        if (testng.isFile()) MinioArtifactUploader.uploadArtifact(testng.getPath(), prefix + "testng-results.xml");
    }
}

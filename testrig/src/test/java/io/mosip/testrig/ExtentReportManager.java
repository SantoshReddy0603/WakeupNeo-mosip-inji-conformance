package io.mosip.testrig;

import com.aventstack.extentreports.ExtentReports;
import com.aventstack.extentreports.ExtentTest;
import com.aventstack.extentreports.reporter.ExtentSparkReporter;
import com.aventstack.extentreports.reporter.configuration.Theme;

import java.io.File;

/**
 * Manages ExtentReports lifecycle for the OpenID Conformance Test Rig.
 */
public class ExtentReportManager {
    private static ExtentReports extent;
    private static final ThreadLocal<ExtentTest> testNode = new ThreadLocal<>();

    public static synchronized ExtentReports getInstance(String reportPath) {
        if (extent == null) {
            File reportDir = new File(reportPath).getParentFile();
            if (reportDir != null && !reportDir.exists()) {
                reportDir.mkdirs();
            }

            ExtentSparkReporter spark = new ExtentSparkReporter(reportPath);
            spark.config().setDocumentTitle("Inji OpenID 1.0 Conformance Report");
            spark.config().setReportName("MOSIP Inji Conformance Test Execution");
            spark.config().setTheme(Theme.STANDARD);

            extent = new ExtentReports();
            extent.attachReporter(spark);
            extent.setSystemInfo("Framework", "MOSIP api-testrig");
            extent.setSystemInfo("Standard", "OpenID4VCI & OpenID4VP 1.0");
            extent.setSystemInfo("Environment", System.getProperty("env.endpoint", "Local Docker"));
        }
        return extent;
    }

    public static void setTest(ExtentTest test) {
        testNode.set(test);
    }

    public static ExtentTest getTest() {
        return testNode.get();
    }

    public static synchronized void flush() {
        if (extent != null) {
            extent.flush();
        }
    }
}

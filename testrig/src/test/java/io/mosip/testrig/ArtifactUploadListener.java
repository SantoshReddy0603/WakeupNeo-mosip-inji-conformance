package io.mosip.testrig;

import org.testng.IExecutionListener;

/** Runs after TestNG has written reports, including failure reports. */
public class ArtifactUploadListener implements IExecutionListener {
    @Override
    public void onExecutionFinish() {
        OpenIDConformanceTest.uploadCompletedArtifacts();
    }
}

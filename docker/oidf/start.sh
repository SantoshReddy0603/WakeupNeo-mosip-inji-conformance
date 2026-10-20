#!/bin/sh
set -eu
# Trust the generated development TLS certificate without disabling validation.
if [ -f /local-trust/server.crt ]; then
  cp "$JAVA_HOME/lib/security/cacerts" /tmp/inji-cacerts
  keytool -importcert -noprompt -alias local-inji-conformance -file /local-trust/server.crt \
    -keystore /tmp/inji-cacerts -storepass changeit
  export JAVA_TOOL_OPTIONS="${JAVA_TOOL_OPTIONS:-} -Djavax.net.ssl.trustStore=/tmp/inji-cacerts -Djavax.net.ssl.trustStorePassword=changeit"
fi
exec java -Djdk.tls.maxHandshakeMessageSize=65536 -jar /server/fapi-test-suite.jar

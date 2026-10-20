FROM injistack/inji-certify-with-plugins:1.0.0-alpha.1@sha256:1579b2449f1a7213fe25de1f6a1509b5636f1fedf0d7f5c4cfd07b9f0fc5b346 AS upstream
FROM python:3.12-slim AS assemble
COPY --from=upstream /home/inji/certify-service.jar /original.jar
COPY certify-core.jar /core.jar
COPY replace_core.py /replace_core.py
RUN python /replace_core.py /original.jar /core.jar /certify-service.jar
FROM upstream
USER root
COPY --from=assemble /certify-service.jar /home/inji/certify-service.jar
# This local issuer uses only the actual PostgreSQL data provider.
RUN rm /home/inji/additional_jars/mock-certify-plugin.jar \
       /home/inji/additional_jars/mosip-identity-certify-plugin.jar \
       /home/inji/additional_jars/sunbird-rc-certify-integration-impl.jar \
    && chown inji:inji /home/inji/certify-service.jar
LABEL org.opencontainers.image.description="Native Certify request-extension fix, pinned release plus reviewed source patch"
USER 1001

FROM maven:3.9-eclipse-temurin-21 AS build
ARG OIDF_REF
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
RUN git init && git remote add origin https://gitlab.com/openid/conformance-suite.git && git fetch --depth=1 origin ${OIDF_REF} && git checkout --detach FETCH_HEAD
RUN --mount=type=cache,target=/root/.m2 mvn -B -DskipTests package

FROM eclipse-temurin:21-jre
COPY --from=build /build/target/fapi-test-suite.jar /server/fapi-test-suite.jar
EXPOSE 8080
COPY start.sh /server/start.sh
ENTRYPOINT ["sh", "/server/start.sh"]

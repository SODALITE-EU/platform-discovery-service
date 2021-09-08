FROM openjdk:11.0.8-jre-buster as builder
WORKDIR /build/
COPY . /build/
RUN /build/generate.sh


FROM python:alpine3.13
WORKDIR /app
COPY requirements.txt /app/

RUN apk add openssh openssl-dev openssh-client

RUN export CRYPTOGRAPHY_PREREQS="gcc musl-dev libffi-dev  python3-dev cargo" \
    && export PIP_PREREQS="git" \
    && apk add $CRYPTOGRAPHY_PREREQS $PIP_PREREQS \
    && pip3 install --no-cache-dir wheel \
    && pip3 install --no-cache-dir -r requirements.txt \
    && apk del $CRYPTOGRAPHY_PREREQS $PIP_PREREQS \
    && rm requirements.txt

COPY --from=builder /build/src/ /app/
COPY /blueprints /blueprints
ENV PDS_BLUEPRINT_PATH="/blueprints"

# install standard ansible collections
COPY requirements.yml .
RUN ansible-galaxy install -r requirements.yml \
    && rm requirements.yml

# install custom ansible collections
COPY /src/ansible_collections /ansible_collections

WORKDIR /ansible_collections/sodalite/discovery/
RUN ansible-galaxy collection build --force \
    && ansible-galaxy collection install sodalite-discovery-0.1.0.tar.gz --force

WORKDIR /ansible_collections/sodalite/hpc/
RUN ansible-galaxy collection build --force \
    && ansible-galaxy collection install sodalite-hpc-0.1.0.tar.gz --force  

WORKDIR /app
ENTRYPOINT ["python3"]
CMD ["-m", "pds.api.run"]
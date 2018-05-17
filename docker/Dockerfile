# Pulling Base image
FROM ubuntu:16.04

# Installing requisites
RUN apt-get update \
  && apt-get -y install software-properties-common \
  && add-apt-repository ppa:webupd8team/java \
  && apt-get update \
  && echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections \
  && apt-get -y install oracle-java8-installer

# Adding JAVA HOME Variable
ENV JAVA_HOME="/usr/lib/jvm/java-8-oracle/jre/bin/java"

# COPYING
COPY lu4r-0.2.1_ /root

# Workdirectory
WORKDIR /root

# Default command
#CMD ["bash"]
CMD ["java","-jar","-Xmx1G","lu4r.jar","basic","cfr", "en", "9090"]

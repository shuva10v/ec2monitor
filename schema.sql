CREATE DATABASE IF NOT EXISTS ec2monitor;

CREATE TABLE IF NOT EXISTS InstanceLog(
  client VARCHAR(255),
  checkTime DATETIME,
  region VARCHAR(255),
  instanceId VARCHAR(255),
  platform VARCHAR(255),
  imageId VARCHAR(255),
  instanceType VARCHAR(255),
  cpuCoreCount INT,
  cpuThreadsPerCore INT,
  state VARCHAR(255),
  tenancy VARCHAR(255),
  launchTime DATETIME
);

CREATE TABLE IF NOT EXISTS InstanceState(
  client VARCHAR(255),
  checkTime DATETIME,
  region VARCHAR(255),
  instanceId VARCHAR(255),
  platform VARCHAR(255),
  imageId VARCHAR(255),
  instanceType VARCHAR(255),
  cpuCoreCount INT,
  cpuThreadsPerCore INT,
  state VARCHAR(255),
  tenancy VARCHAR(255),
  launchTime DATETIME,
  PRIMARY KEY (instanceId)
);


This folder contains snippets in basic Java applications that perfom some basic DICOM operations using [dcm4che](https://github.com/dcm4che/dcm4che) library.

In `pom.xml`, add new repository
```xml
<repositories>
   <repository>
      <id>www.dcm4che.org</id>
      <name>dcm4che Repository</name>
      <url>http://www.dcm4che.org/maven2</url>
   </repository>
</repositories>
```
and dependency
```xml
<dependency>
   <groupId>org.dcm4che.tool</groupId>
   <artifactId>dcm4che-tool-all</artifactId>
   <version>3.3.8</version>
   <type>pom</type>
</dependency>
```

The snippets are:

* [Test DICOM connection (C-ECHO)](EchoApp.md)

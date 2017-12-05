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

* Test DICOM connection (C-ECHO) :

  Run the [EchoApp](EchoApp.java) program, it will output (if success):
  ```
  (0000,0002) UI [1.2.840.10008.1.1] AffectedSOPClassUID
  (0000,0100) US [32816] CommandField
  (0000,0120) US [1] MessageIDBeingRespondedTo
  (0000,0800) US [257] CommandDataSetType
  (0000,0900) US [0] Status
  ```

* [Get all SOPInstanceUID from a Study/Patient (C-FIND)](RetrieveStudy.md)

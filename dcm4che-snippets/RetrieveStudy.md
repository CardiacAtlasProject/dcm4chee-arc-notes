# Query all SOPInstanceUIDs from a Patient/Study

This document shows how to use C-FIND using dcm4che library to get all SOPInstanceUIDs (reference to DICOM image files) from a Patient/Study. DICOM operations for this is a bit tricky. You have to hierarchically use C-FIND messages (or **`findscu`** tool) from Study -> Series -> Images.

Another trouble is that the SCP (Service Class Provider) will send the query results as DICOM files. You need to extract the information you want from their headers. You can also use `findscu` option to save the output as XML file, or you can use `dcm2json` tool to convert the header into JSON format.

Let's do it hierarchically.

Assume `calledAET=DCM4CHEE`, `hostname=localhost` and `port=11112`.

## Query all SeriesInstanceUIDs from a StudyInstanceUID

You need both PatientID and StudyInstanceUID. Assume:

* `PatientID=PAT0001`
* `StudyInstanceUID=2.16.124.113543.6006.99.3269191020737436947`

and you just want to get SeriesInstanceUID, nothing else. 

With `findscu` CLI, the command is:
```bash
$ findscu -c DCM4CHEE@localhost:11112 -L SERIES -M PatientRoot -m PatientID=PAT0001 -m StudyInstanceUID=2.16.124.113543.6006.99.3269191020737436947 --out-dir . --out-file series- -X -r SeriesInstanceUID
```

On success, this command will result a number of XML files (because of `-X` option) for each series in the current directory (`--out-dir` option). Each file will prefixed by `series-` (`--out-file` option).

## Query all SOPInstanceUIDs (image files) from a SeriesInstanceUID

Once you have known PatientID, StudyInstanceUID and SeriesInstanceUID, you can retrieve all SOPInstanceUIDs, which refer to a DICOM image file.

Assume:
* `PatientID=PAT0001`
* `StudyInstanceUID=2.16.124.113543.6006.99.3269191020737436947`
* `SeriesInstanceUID=2.16.124.113543.6006.99.1023448225987074702`

The command is:
```bash
$ findscu -c DCM4CHEE@localhost:11112 -L IMAGE -M PatientRoot -m PatientID=PAT0001 -m StudyInstanceUID=2.16.124.113543.6006.99.3269191020737436947 -m SeriesInstanceUID=2.16.124.113543.6006.99.1023448225987074702 --out-dir . --out-file images- -X -r SOPInstanceUID
```

## Implementing in JAVA

The **`FindSCU`** class in dcm4che library only outputs either DICOM or XML files as a result of findSCU command. I have made a simpler [QueryDICOM](QueryDICOM.java) class that handles all the necessary associations and attributes. The [DICOMTransferHandle](DICOMTransferHandle.java) class overrides the default findSCU handle to retrieve results, which only print the returned attributes.

An example to retrieve all SeriesInstanceUIDs
```java
try {
  QueryDICOM qr = new QueryDICOM()
    .setCalledAET("DCM4CHEE")
    .setHostname("localhost")
    .setPort(11112)
    .setRetrieveLevel(QueryDICOM.LevelType.SERIES)
    .addQueryAttribute("StudyInstanceUID", "2.16.124.113543.6006.99.3269191020737436947")
    .addQueryAttribute("PatientID", "PAT0001");
			
    // let's return SeriesInstanceUID and SeriesDescription
    qr.addReturnAttributes("SeriesInstanceUID", "SeriesDescription");
			
    System.out.println("Attributes sent to SCP. Empty attributes are going to be returned by SCP.");
    System.out.println(qr.getKeys());
			
    System.out.println("Attributes returned by SCP:");
    qr.execute();
			
  } catch( Exception e ) {
    System.err.println("findscu: " + e.getMessage());
    e.printStackTrace();
    System.exit(2);
}
```

The output:
```
Attributes sent to SCP. Empty attributes are going to be returned by SCP.
(0008,0052) CS [SERIES] QueryRetrieveLevel
(0008,103E) LO [] SeriesDescription
(0010,0020) LO [PAT0001] PatientID
(0020,000D) UI [2.16.124.113543.6006.99.3269191020737436947] StudyInstanceUID
(0020,000E) UI [] SeriesInstanceUID

Attributes returned by SCP:
(0008,0005) CS [ISO_IR 100] SpecificCharacterSet
(0008,0052) CS [SERIES] QueryRetrieveLevel
(0008,0054) AE [DCM4CHEE] RetrieveAETitle
(0008,0056) CS [ONLINE] InstanceAvailability
(0008,103E) LO [SHORT-AXIS] SeriesDescription
(0010,0020) LO [PAT0001] PatientID
(0020,000D) UI [2.16.124.113543.6006.99.3269191020737436947] StudyInstanceUID
(0020,000E) UI [2.16.124.113543.6006.99.1023448225987074702] SeriesInstanceUID

(0008,0005) CS [ISO_IR 100] SpecificCharacterSet
(0008,0052) CS [SERIES] QueryRetrieveLevel
(0008,0054) AE [DCM4CHEE] RetrieveAETitle
(0008,0056) CS [ONLINE] InstanceAvailability
(0008,103E) LO [SCOUT IMAGING] SeriesDescription
(0010,0020) LO [PAT0001] PatientID
(0020,000D) UI [2.16.124.113543.6006.99.3269191020737436947] StudyInstanceUID
(0020,000E) UI [2.16.124.113543.6006.99.1902359864559460223] SeriesInstanceUID

(0008,0005) CS [ISO_IR 100] SpecificCharacterSet
(0008,0052) CS [SERIES] QueryRetrieveLevel
(0008,0054) AE [DCM4CHEE] RetrieveAETitle
(0008,0056) CS [ONLINE] InstanceAvailability
(0008,103E) LO [SCOUT] SeriesDescription
(0010,0020) LO [PAT0001] PatientID
(0020,000D) UI [2.16.124.113543.6006.99.3269191020737436947] StudyInstanceUID
(0020,000E) UI [2.16.124.113543.6006.99.6175936712814978825] SeriesInstanceUID
```

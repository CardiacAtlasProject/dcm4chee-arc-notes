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


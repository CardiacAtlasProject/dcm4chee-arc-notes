Two important links:

* [RESTful services from DCM4CHEE-ARC](http://petstore.swagger.io/index.html?url=https://raw.githubusercontent.com/dcm4che/dcm4chee-arc-light/master/dcm4chee-arc-ui2/src/swagger/swagger.json)
* [RESTful services from DICOM](http://petstore.swagger.io/index.html?url=https://raw.githubusercontent.com/dcm4che/dcm4chee-arc-light/master/dcm4chee-arc-ui2/src/swagger/swagger-dicom.json)

Assuming that
* `AET=DCM4CHEE`
* `localhost`
* port=8080

Some examples:

1. Show the status of the archive:
```
$ curl -X GET "http://localhost:8080/dcm4chee-arc/ctrl/status" -H "accept: application/json"
[{
    "status": "STARTED"
}]
```

2. List application entities:
```
$ curl -X GET "http://localhost:8080/dcm4chee-arc/aes" -H "accept: application/json"
[
    {
        "dicomAETitle": "DCM4CHEE",
        "dicomAssociationAcceptor": true,
        "dicomAssociationInitiator": true,
        "dicomDescription": "Hide instances rejected for Quality Reasons",
        "dicomDeviceName": "dcm4chee-arc",
        "dicomNetworkConnection": [
            {
                "dicomHostname": "localhost",
                "dicomPort": 11112
            }
        ]
    },
    {
        "dicomAETitle": "DCM4CHEE_ADMIN",
        "dicomAssociationAcceptor": true,
        "dicomAssociationInitiator": true,
        "dicomDescription": "Show instances rejected for Quality Reasons",
        "dicomDeviceName": "dcm4chee-arc",
        "dicomNetworkConnection": [
            {
                "dicomHostname": "localhost",
                "dicomPort": 11112
            }
        ]
    },
    {
        "dicomAETitle": "DCM4CHEE_TRASH",
        "dicomAssociationAcceptor": true,
        "dicomAssociationInitiator": true,
        "dicomDescription": "Show rejected instances only",
        "dicomDeviceName": "dcm4chee-arc",
        "dicomNetworkConnection": [
            {
                "dicomHostname": "localhost",
                "dicomPort": 11112
            }
        ]
    },
    {
        "dicomAETitle": "SCHEDULEDSTATION",
        "dicomAssociationAcceptor": true,
        "dicomAssociationInitiator": true,
        "dicomDeviceName": "scheduledstation",
        "dicomNetworkConnection": [
            {
                "dicomHostname": "localhost",
                "dicomPort": 104
            }
        ]
    }
]
```

3. List application entity titles
```
$ curl -X GET "http://localhost:8080/dcm4chee-arc/aets" -H "accept: application/json"
[
    {
        "dcmAcceptedUserRole": [
            "user",
            "admin"
        ],
        "description": "Hide instances rejected for Quality Reasons",
        "title": "DCM4CHEE"
    },
    {
        "dcmAcceptedUserRole": [
            "admin"
        ],
        "description": "Show instances rejected for Quality Reasons",
        "title": "DCM4CHEE_ADMIN"
    },
    {
        "dcmAcceptedUserRole": [
            "admin"
        ],
        "dcmHideNotRejectedInstances": true,
        "description": "Show rejected instances only",
        "title": "DCM4CHEE_TRASH"
    }
]
```

4. Show storage location
```
$ curl -X GET "http://localhost:8080/dcm4chee-arc/storage" -H "accept: application/json"
[
    {
        "dcmDigestAlgorithm": "MD5",
        "dcmInstanceAvailability": "ONLINE",
        "dcmProperty": [
            "pathFormat={now,date,yyyy/MM/dd}/{0020000D,hash}/{0020000E,hash}/{00080018,hash}",
            "checkMountFile=NO_MOUNT"
        ],
        "dcmStorageID": "fs1",
        "dcmURI": "file:/opt/ARCHIVE/",
        "dicomAETitle": [
            "DCM4CHEE"
        ],
        "usages": [
            "dcmObjectStorageID"
        ]
    }
]
```

5. Store an image file `image-test.dcm` using STOW-RS service without study id:
```
$ curl -X POST "http://localhost:8080/dcm4chee-arc/aets/DCM4CHEE/rs/studies" -H "Content-Type: multipart/related;type=application/dicom" -F "content=@image-test.dcm; type=application/dicom"
```

The StudyID and PatientID were inferred from the DICOM header and created. The log:
```
12:53:30,946 INFO  [org.dcm4chee.arc.stow.StowRS] (default task-8) Process POST /dcm4chee-arc/aets/DCM4CHEE/rs/studies from null@10.0.2.2
12:53:30,974 INFO  [org.dcm4chee.arc.stow.StowRS] (default task-8) storeInstances: Extract Part #1{content-disposition=[form-data; name=content; filename=image-test.dcm], content-type=[application/dicom]}
12:53:31,650 INFO  [org.dcm4chee.arc.patient.impl.PatientServiceEJB] (default task-8) 10.0.2.2: Create Patient[pk=1, id=PatientID[pk=1, id=SCD0001201, issuer=null], name=SCD0001201]
12:53:31,827 INFO  [org.dcm4chee.arc.store.impl.StoreServiceImpl] (default task-8) null@10.0.2.2->DCM4CHEE: Create Study[pk=1, uid=2.16.124.113543.6006.99.3958034689711867127, id=*]
12:53:31,882 INFO  [org.dcm4chee.arc.store.impl.StoreServiceImpl] (default task-8) null@10.0.2.2->DCM4CHEE: Create Series[pk=1, uid=2.16.124.113543.6006.99.3959268667708052213, no=2, mod=MR]
12:53:31,897 INFO  [org.dcm4chee.arc.store.impl.StoreServiceImpl] (default task-8) null@10.0.2.2->DCM4CHEE: Create Instance[pk=1, uid=2.16.124.113543.6006.99.08330918210882751671, class=1.2.840.10008.5.1.4.1.1.4, no=22]
```

6. Deleting a study

   You can only delete a patient or study if they are empty. Otherwise you must reject the study first before permanently delete it. To reject a patient, you must supply the rejection code and the coding scheme. Here's how you get possible rejection notes:
   ```
   $ curl GET "http://localhost:8080/dcm4chee-arc/reject" -H "accept: application/json" | python -m json.tool
   [
    {
        "codeMeaning": "Rejected for Quality Reasons",
        "codeValue": "113001",
        "codingSchemeDesignator": "DCM",
        "label": "Quality",
        "type": "REJECTED_FOR_QUALITY_REASONS"
    },
    {
        "codeMeaning": "Rejected for Patient Safety Reasons",
        "codeValue": "113037",
        "codingSchemeDesignator": "DCM",
        "label": "Patient Safety",
        "type": "REJECTED_FOR_PATIENT_SAFETY_REASONS"
    },
    {
        "codeMeaning": "Incorrect Modality Worklist Entry",
        "codeValue": "113038",
        "codingSchemeDesignator": "DCM",
        "label": "Incorrect MWL Entry",
        "type": "INCORRECT_MODALITY_WORKLIST_ENTRY"
    },
    {
        "codeMeaning": "Data Retention Policy Expired",
        "codeValue": "113039",
        "codingSchemeDesignator": "DCM",
        "label": "Retention Expired",
        "type": "DATA_RETENTION_POLICY_EXPIRED"
    }
   ]
   ```

   1. Reject a study, e.g. using REJECTED_FOR_QUALITY_REASONS:
      ```
      $ curl -X POST "http://localhost:8080/dcm4chee-arc/aets/DCM4CHEE/rs/studies/2.16.124.113543.6006.99.3958034689711867127/reject/113001^DCM" -H "accept: application/json"
      ```

   2. Delete permanently
      ```
      $ curl -X DELETE "http://localhost:8080/dcm4chee-arc/reject/113001^DCM" -H "accept: application/json"
      ```

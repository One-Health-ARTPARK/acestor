# Line List Data Dictionary v0.1.0

### Author(s)
- [Sneha S](https://github.com/snehasaisneha)
- [Gagan Goutham](https://github.com/GaganGoutham)

The fields in the line list are divided into 4 categories.
Do note that this version is still in alpha, and might be changed.

1. metadata
2. demographics
3. location
4. events

### METADATA
| field                | description                                                                      | comments                                                                                                                             |
| -------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| metadata.ID          | UUID for the given linelist record. based on UUID4 from python3. Not yet stable. | patients with repeat infections can have multiple entries, and this cannot be verified as the entries are deidentified.              |
| metadata.primaryDate | primary date associated with the case. Compliant with ISO 8601 format.           | calculated based on dates available, event.symptomOnset.date given preference, followed by event.test.date and event.test.resultDate |

### DEMOGRAPHICS

| field                 | description                                                                                        | comments                                                                                                       |
| --------------------- | -------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| demographics.age      | age of patient, np.float, range - (0,120]. will be deprecated in the future in favour of ageRange. | \-                                                                                                             |
| demographics.ageRange | string, one of 0-5, 6-12, 13-18, 19-44, 45-64, 65+. inclusive of both limits (Except 0).           | ages above 120 are automatically rejected. this is not yet stable as the selected age brackets are not frozen. |
| demographics.gender   | one of [MALE, FEMALE, NON-BINARY/THIRD GENDER, OTHER, UNKNOWN]                                     | \-                                                                                                             |

### LOCATION

| field                           | description                                                                                                                                                                                | comments                                                                                                                                               |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| location.country.ID             | country ID - constructed using ISO 3166 alpha-2 code. e.g. country_IN for India                                                                                                            | \-                                                                                                                                                     |
| location.country.name           | country name from ISO Codes or as per relevant government notification                                                                                                                     | \-                                                                                                                                                     |
| location.admin.hierarchy        | administrative hierarchy used by line list entry - either revenue or ulb in India.                                                                                                         | Different administrative hierarchies are used in different parts of India. Codes detailed at [https://lgdirectory.gov.in](https://lgdirectory.gov.in/) |
| location.admin1.ID              | state ID or union territory ID. Unique across a given country. Constructed using LGD codes in India, from Ministry of Panchayati Raj.                                                      | In India, if a state has LGD code 29, the stateID is state_29. state_-1 if unknown.                                                                    |
| location.admin1.name            | state or UT name, as per LGD                                                                                                                                                               | name as per LGD                                                                                                                                        |
| location.admin2.ID              | district ID, constructed from relevant LGD code.                                                                                                                                           | LGD code 545 results in district_545 as ID. district_-1 if unknown                                                                                     |
| location.admin2.name            | district Name, as per LGD                                                                                                                                                                  | \-                                                                                                                                                     |
| location.admin3.ID              | subdistrict ID or ulb ID, constructed from relevant subdistrict/urban local body LGD code.                                                                                                 | subdistrict_-1 if unknown.                                                                                                                             |
| location.admin3.name            | subdistrict or urban local body name, as per LGD                                                                                                                                           | \-                                                                                                                                                     |
| location.admin4.ID              | if admin3 is subdistrict, then village ID, else if admin3 is ulb, then zone ID. village ID is constructed from LGD, zone ID is constructed based on relevant municipal/state notification. | \-                                                                                                                                                     |
| location.admin4.name            | village Name, as per LGD, or zone name, as notified by the relevant urban local body or state authority                                                                                    | \-                                                                                                                                                     |
| location.admin5.ID              | if admin4 is zoneID, then wardID. ward ID is constructed from relevant municipal/state notification.                                                                                       | \-                                                                                                                                                     |
| location.admin5.name            | ward name, as notified by the relevant urban local body or state authority                                                                                                                 | \-                                                                                                                                                     |
| location.geometry.latitude      | latitude of the address                                                                                                                                                                    | \-                                                                                                                                                     |
| location.geometry.longitude     | longitude of the address                                                                                                                                                                   | \-                                                                                                                                                     |
| location.geometry.coarseness    | coarseness of the latitude/longitude. admin1, admin2, admin3, or address                                                                                                                   | \-                                                                                                                                                     |
| location.healthcenter.PHC       | name of Primary Health Centre associated with case                                                                                                                                         | \-                                                                                                                                                     |
| location.healthcenter.subcenter | name of relevant subcenter associated with case                                                                                                                                            | \-                                                                                                                                                     |
| location.healthcenter.SSH       | Sentinel Surveillance Hospital where case was reported                                                                                                                                     | \-                                                                                                                                                     |

### EVENTS

| field                            | description                                                 | comments                                                               |
| -------------------------------- | ----------------------------------------------------------- | ---------------------------------------------------------------------- |
| event.symptomOnset               | boolean, if symptom onset was recorded                      | usually set to True                                                    |
| event.symptomOnset.date          | date of symptom onset, compliant with the ISO 8601 format.        | usually self reported                                                  |
| event.test                       | True or False                                               | \-                                                                     |
| event.test.sampleCollectionDate  | date of test, compliant with ISO 8601 format                | \-                                                                     |
| event.test.type                  | string                                                      | for dengue, can be NS1 Ag ELISA, IgM ELISA, IgG ELISA, PCR, or Unknown |
| event.test.resultDate            | date of test result, compliant with ISO 8601 format.               |                                                                        |
| event.test.result                | boolean, True for positive test and False for negative test | \`                                                                     |
| event.test.value                 | value of test result, np.float64                            |                                                                        |
| event.test.numberOfTests         | number of tests, np.int32                                   | can be more than one in case of NS1/IgM/IgG panel                      |
| event.test.additionalTests.notes | notes in case a panel of tests was performed.               | \-                                                                     |

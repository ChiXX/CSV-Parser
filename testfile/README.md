# Coding task for programmer candidates at SAGA Diagnostics

We are pleased that you are considering SAGA Diagnostics as a potential future employer. Below you will find description of the task and instructions on how to submit the result.

## Objective
The task is to develop web application in Python using Flask framework with one API endpoint and one view and ideally deploy the app on any cloud-services provider (or at least provide docker image for it). The application will accept a text file in a specific format, extract information from the file, add selected entries to internal storage/DB and then show the entries on the view page.


## Specifications
### API endpoint

The application API end-point should be accessible at `yyyy.xxx:pppp/api` (where `yyy.xxx` is IP/hostname/localhost and `pppp` is a port) and it should accept POST requests for uploading a text file. So it is possible to upload `example.csv` file via command:

```
curl -H "Content-Type: text/csv" --data-binary "@example.csv" yyyy.xxx:pppp/api
```


### Backend
* check that file conforms to specifications:
    - tab delimited
    - has #chrom1, start1, end1, chrom2, end2, sample, score columns
* get only top 10 lines per sample (with highest score) and save to a persistent storage.
* database should only contain 10 lines per uniq sample, if a file with new lines for the sample is uploaded the previous entries should be overwritten.
This also can be achieved by importing all the lines into the database and then outputting only latest top 10 entries per sample in the view.
* database implementation is optional can be anything (flat file, SQLite, etc).

### Frontend

* one view accessible at `yyyy.xxx:pppp/view` address, which shows top 10 (based on highest score) lines per unique sample.
* table should be sortable for `sample` and score `column`


### Optional

* add authentication to the app

## Deployment and submission

* app source code should be saved in a private repository and shared with Robert (robert.rigo@sagadiagnostics.com) and Sergii (sergii.gladchuk@sagadiagnostics.com).
* the functional app should be containerized and ideally deployed to any of the cloud service providers (AWS, Azure, GoogleCloud) and IP/hostname to access the app sharedwith Robert (robert.rigo@sagadiagnostics.com) and Sergii (sergii.gladchuk@sagadiagnostics.com).
* in case the above is not possible container image is enough or detailed instructions on how to create one should be provided in the repository's README.md.
* instructions should also include how to make a POST request to the app (ideally with curl, and especially if authentication was added)

## Final notes

Feel free to add any other features or improvements to this small app, and leave as many comments as you 
think is appropriate to communicate your choices of design.

Good luck and have fun solving this non-trivial task!
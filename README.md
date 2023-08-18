# CSV-Parser

The program uses Flask as the backend framework. It has authentication. Users can upload csv file with specified mandatory columns and sort and group based on column names. Tables and their operations can be stored in a sql database. The application provides two api end points for sign up and file upload.

## APP functionality

### Authentication

When registering a new user, the email will be checked to see if it's already registered. There are also checks for the length of the username and password.

Later User can then log in with email and password.

### File uploading

Files must have either a `.csv` or `.tsv` extension, and their contents must be separated by `,` or `\t`. During file upload, there will be verification to check if a file with the same name already exists in the current user's database. Uploading a file with the same name as an existing file is not allowed. The header of the table must include columns named `chrom1`, `start1`, `end1`, `chrom2`, `end2`, `sample`, and `score`.

User can upload multiple files and then choose one of them to perform operations on.

### File operation

Users can group the table by `chrom1`, `chrom2` and `sample` columns, and sort the table by all columns. Users can also specify to display the first 5, 10, 15, or 20 rows. Once the settings are configured, users can click the "Save and Apply" button to perform the corresponding operations on the file. The settings will be saved to database as well.

## API

### Sign up

When sign up, email, user name and password must be provided.

```bash
curl -X POST -H "Content-Type: application/json" -d '{"email": "test@test", "name": "test", "password": "1234"}' http://127.0.0.1:5000/api/signup
```

### Uploading file

A registered email and password is needed when uploading file. 

```bash
curl.exe -H "Content-Type: text/csv" -H "filename: example.csv" --data-binary "@testfile/example.csv" -u test@test:1234 127.0.0.1:5000/api/upload
```

## Docker image

A Docker file is provided. And the image is available from docker hub.

```bash
docker pull bionamicxu/csv-parser:latest
docker run -p 5000:5000 csv-parser-image
```

Or the image can be built by:

```bash
git clone git@github.com:ChiXX/CSV-Parser.git
docker build -t csv-parser-image .
```

The app will run on `http://127.0.0.1:5000/`


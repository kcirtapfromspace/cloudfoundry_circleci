# SAP Cloud Platform - Cloud Foundry - Python - Docker - Sample Application
[![CircleCI](https://dl.circleci.com/status-badge/img/gh/kcirtapfromspace/cloudfoundry_circleci/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/kcirtapfromspace/cloudfoundry_circleci/tree/main)

## Prerequisites
### Cloud Foundry CLI (SAP 90 day trial)
Get a free trial account on [SAP Cloud Platform](https://developers.sap.com/tutorials/hcp-create-trial-account.html)

Grab Cloud Foundry Envionment details
API Endpoint: [https://api.cf.us10-001.hana.ondemand.com](https://api.cf.us10-001.hana.ondemand.com)
Org Name: `c44fa123trial`
Org ID: `220fb074-bdf1-489f-b6ba-0f32e7e9054a`

### CircleCI
Get a free account on CircleCI
[circle ci][circle ci]
bootstrap your project with CircleCI

#### View the CircleCI pipeline
[https://app.circleci.com/pipelines/github/kcirtapfromspace/cloudfoundry_circleci](https://app.circleci.com/pipelines/github/kcirtapfromspace/cloudfoundry_circleci)

### Github
Create a new repository on Github

#### Bot Account
Create a bot account on Github
this can be as easy as adding `+bot_account` to your email address to create a new account
`<email>+bot_account@gmail.com`

Once that account is created you can add it as a collaborator to your repository.
Sign in to your bot account and accept the invitation to collaborate.


Follow steps in [Personal Access Token(classic)](#personal-access-tokenclassic) to create a PAT for your bot account.


#### Deploy Key
Authenticating CircleCI server to commit the artifact (e.g., report, plot, documentation) generated by CircleCI job on your behalf to GitHub.

When we authenticate CircleCI to build a GitHub repository for the first time, it adds a Read-Only deploy key to our GitHub repo. This can be found in GitHub Repo → Settings → Deploy Keys

#### Personal Access Token(classic)
Create a new Personal Access Token(classic) with `repo` and `write:packages` permissions

Generate a GitHub PAT, either for your own account or a bot account, with the required scope to write to your repository (public_repo for a public repository, repo for a private repository) and write:packages for GitHub Packages. This token will be used to authenticate the CircleCI server to push the Docker image to GitHub Packages.

[refer GitHub PAT generation](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token)
You would then define this as an environment variable in your CircleCI build (e.g., GITHUB_PAT) in the Project Settings → Environment Variables → Add Environment Variable.

This would authenticate you to push to your repository using the following URL pattern: https://workflowr:$GITHUB_PAT@github.com/<account>/<repo>.git.

It is not possible to limit the scope of a PAT to a single repository. In other words, if a PAT with write permissions is exposed, it gives write access to every repository owned by that account. Therefore, it is recommended to create a separate GitHub account for CircleCI to use, and give it access to only the repositories that it needs to push to.

## The Dirt of it

### Docker
Create circleci to build docker images and publish to github packages

```
$ export GH_BOT_PAT=YOUR_TOKEN
$ echo $GH_BOT_PAT | docker login ghcr.io -u USERNAME --password-stdin

Login Succeeded
```

### Cloud Foundry
#### Create a postgres service instance
```
$ cf create-service postgresql-db trial pg-instance-trial
```

#### Create a service key for the postgres service instance
```
$ cf create-service-key pg-instance-trial pg-instance-trial-key
```

#### View the service key
```
$ cf service-key pg-instance-trial pg-service-key | jq -R 


"Getting key pg-service-key for service instance pg-instance-trial as patrickdeutsch@gmail.com..."
""
"{"
"  \"credentials\": {"
"    \"dbname\": \"wOPeoZIbVhnG\","
"    \"hostname\": \"postgres-ba8904b8-bdeb-4268-9915-66c52ad76462.cqryblsdrbcs.us-east-1.rds.amazonaws.com\","
"    \"password\": \"b81da0190535\","
"    \"port\": \"6275\","
"    \"sslcert\": \"-----BEGIN CERTIFICATE-----\\nMIIEBzCCAu+gAwIBAgICJVUwDQYJKoZIhvcNAQELBQAwgY8xCzAJBgNVBAYTAlVT\\nMRAwDgYDVQQHDAdTZWF0dGxlMRMwEQYDVQQIDApXYXNoaW5ndG9uMSIwIAYDVQQK\\nDBlBbWF6b24gV2ViIFNlcnZpY2VzLCBJbmMuMRMwEQYDVQQLDApBbWF6b24gUkRT\\nMSAwHgYDVQQDDBdBbWF6b24gUkRTIFJvb3QgMjAxOSBDQTAeFw0xOTA5MTkxODE2\\nNTNaFw0yNDA4MjIxNzA4NTBaMIGUMQswCQYDVQQGEwJVUzETMBEGA1UECAwKV2Fz\\naGluZ3RvbjEQMA4GA1UEBwwHU2VhdHRsZTEiMCAGA1UECgwZQW1hem9uIFdlYiBT\\nZXJ2aWNlcywgSW5jLjETMBEGA1UECwwKQW1hem9uIFJEUzElMCMGA1UEAwwcQW1h\\nem9uIFJEUyB1cy1lYXN0LTEgMjAxOSBDQTCCASIwDQYJKoZIhvcNAQEBBQADggEP\\nADCCAQoCggEBAM3i/k2u6cqbMdcISGRvh+m+L0yaSIoOXjtpNEoIftAipTUYoMhL\\nInXGlQBVA4shkekxp1N7HXe1Y/iMaPEyb3n+16pf3vdjKl7kaSkIhjdUz3oVUEYt\\ni8Z/XeJJ9H2aEGuiZh3kHixQcZczn8cg3dA9aeeyLSEnTkl/npzLf//669Ammyhs\\nXcAo58yvT0D4E0D/EEHf2N7HRX7j/TlyWvw/39SW0usiCrHPKDLxByLojxLdHzso\\nQIp/S04m+eWn6rmD+uUiRteN1hI5ncQiA3wo4G37mHnUEKo6TtTUh+sd/ku6a8HK\\nglMBcgqudDI90s1OpuIAWmuWpY//8xEG2YECAwEAAaNmMGQwDgYDVR0PAQH/BAQD\\nAgEGMBIGA1UdEwEB/wQIMAYBAf8CAQAwHQYDVR0OBBYEFPqhoWZcrVY9mU7tuemR\\nRBnQIj1jMB8GA1UdIwQYMBaAFHNfYNi8ywOY9CsXNC42WqZg/7wfMA0GCSqGSIb3\\nDQEBCwUAA4IBAQB6zOLZ+YINEs72heHIWlPZ8c6WY8MDU+Be5w1M+BK2kpcVhCUK\\nPJO4nMXpgamEX8DIiaO7emsunwJzMSvavSPRnxXXTKIc0i/g1EbiDjnYX9d85DkC\\nE1LaAUCmCZBVi9fIe0H2r9whIh4uLWZA41oMnJx/MOmo3XyMfQoWcqaSFlMqfZM4\\n0rNoB/tdHLNuV4eIdaw2mlHxdWDtF4oH+HFm+2cVBUVC1jXKrFv/euRVtsTT+A6i\\nh2XBHKxQ1Y4HgAn0jACP2QSPEmuoQEIa57bEKEcZsBR8SDY6ZdTd2HLRIApcCOSF\\nMRM8CKLeF658I0XgF8D5EsYoKPsA+74Z+jDH\\n-----END CERTIFICATE-----\\n-----BEGIN CERTIFICATE-----\\nMIIEBjCCAu6gAwIBAgIJAMc0ZzaSUK51MA0GCSqGSIb3DQEBCwUAMIGPMQswCQYD\\nVQQGEwJVUzEQMA4GA1UEBwwHU2VhdHRsZTETMBEGA1UECAwKV2FzaGluZ3RvbjEi\\nMCAGA1UECgwZQW1hem9uIFdlYiBTZXJ2aWNlcywgSW5jLjETMBEGA1UECwwKQW1h\\nem9uIFJEUzEgMB4GA1UEAwwXQW1hem9uIFJEUyBSb290IDIwMTkgQ0EwHhcNMTkw\\nODIyMTcwODUwWhcNMjQwODIyMTcwODUwWjCBjzELMAkGA1UEBhMCVVMxEDAOBgNV\\nBAcMB1NlYXR0bGUxEzARBgNVBAgMCldhc2hpbmd0b24xIjAgBgNVBAoMGUFtYXpv\\nbiBXZWIgU2VydmljZXMsIEluYy4xEzARBgNVBAsMCkFtYXpvbiBSRFMxIDAeBgNV\\nBAMMF0FtYXpvbiBSRFMgUm9vdCAyMDE5IENBMIIBIjANBgkqhkiG9w0BAQEFAAOC\\nAQ8AMIIBCgKCAQEArXnF/E6/Qh+ku3hQTSKPMhQQlCpoWvnIthzX6MK3p5a0eXKZ\\noWIjYcNNG6UwJjp4fUXl6glp53Jobn+tWNX88dNH2n8DVbppSwScVE2LpuL+94vY\\n0EYE/XxN7svKea8YvlrqkUBKyxLxTjh+U/KrGOaHxz9v0l6ZNlDbuaZw3qIWdD/I\\n6aNbGeRUVtpM6P+bWIoxVl/caQylQS6CEYUk+CpVyJSkopwJlzXT07tMoDL5WgX9\\nO08KVgDNz9qP/IGtAcRduRcNioH3E9v981QO1zt/Gpb2f8NqAjUUCUZzOnij6mx9\\nMcZ+9cWX88CRzR0vQODWuZscgI08NvM69Fn2SQIDAQABo2MwYTAOBgNVHQ8BAf8E\\nBAMCAQYwDwYDVR0TAQH/BAUwAwEB/zAdBgNVHQ4EFgQUc19g2LzLA5j0Kxc0LjZa\\npmD/vB8wHwYDVR0jBBgwFoAUc19g2LzLA5j0Kxc0LjZapmD/vB8wDQYJKoZIhvcN\\nAQELBQADggEBAHAG7WTmyjzPRIM85rVj+fWHsLIvqpw6DObIjMWokpliCeMINZFV\\nynfgBKsf1ExwbvJNzYFXW6dihnguDG9VMPpi2up/ctQTN8tm9nDKOy08uNZoofMc\\nNUZxKCEkVKZv+IL4oHoeayt8egtv3ujJM6V14AstMQ6SwvwvA93EP/Ug2e4WAXHu\\ncbI1NAbUgVDqp+DRdfvZkgYKryjTWd/0+1fS8X1bBZVWzl7eirNVnHbSH2ZDpNuY\\n0SBd8dj5F6ld3t58ydZbrTHze7JJOd8ijySAp4/kiu9UfZWuTPABzDa/DSdz9Dk/\\nzPW4CXXvhLmE02TA9/HeCw3KEHIwicNuEfw=\\n-----END CERTIFICATE-----\","
"    \"sslrootcert\": \"-----BEGIN CERTIFICATE-----\\nMIIEBzCCAu+gAwIBAgICJVUwDQYJKoZIhvcNAQELBQAwgY8xCzAJBgNVBAYTAlVT\\nMRAwDgYDVQQHDAdTZWF0dGxlMRMwEQYDVQQIDApXYXNoaW5ndG9uMSIwIAYDVQQK\\nDBlBbWF6b24gV2ViIFNlcnZpY2VzLCBJbmMuMRMwEQYDVQQLDApBbWF6b24gUkRT\\nMSAwHgYDVQQDDBdBbWF6b24gUkRTIFJvb3QgMjAxOSBDQTAeFw0xOTA5MTkxODE2\\nNTNaFw0yNDA4MjIxNzA4NTBaMIGUMQswCQYDVQQGEwJVUzETMBEGA1UECAwKV2Fz\\naGluZ3RvbjEQMA4GA1UEBwwHU2VhdHRsZTEiMCAGA1UECgwZQW1hem9uIFdlYiBT\\nZXJ2aWNlcywgSW5jLjETMBEGA1UECwwKQW1hem9uIFJEUzElMCMGA1UEAwwcQW1h\\nem9uIFJEUyB1cy1lYXN0LTEgMjAxOSBDQTCCASIwDQYJKoZIhvcNAQEBBQADggEP\\nADCCAQoCggEBAM3i/k2u6cqbMdcISGRvh+m+L0yaSIoOXjtpNEoIftAipTUYoMhL\\nInXGlQBVA4shkekxp1N7HXe1Y/iMaPEyb3n+16pf3vdjKl7kaSkIhjdUz3oVUEYt\\ni8Z/XeJJ9H2aEGuiZh3kHixQcZczn8cg3dA9aeeyLSEnTkl/npzLf//669Ammyhs\\nXcAo58yvT0D4E0D/EEHf2N7HRX7j/TlyWvw/39SW0usiCrHPKDLxByLojxLdHzso\\nQIp/S04m+eWn6rmD+uUiRteN1hI5ncQiA3wo4G37mHnUEKo6TtTUh+sd/ku6a8HK\\nglMBcgqudDI90s1OpuIAWmuWpY//8xEG2YECAwEAAaNmMGQwDgYDVR0PAQH/BAQD\\nAgEGMBIGA1UdEwEB/wQIMAYBAf8CAQAwHQYDVR0OBBYEFPqhoWZcrVY9mU7tuemR\\nRBnQIj1jMB8GA1UdIwQYMBaAFHNfYNi8ywOY9CsXNC42WqZg/7wfMA0GCSqGSIb3\\nDQEBCwUAA4IBAQB6zOLZ+YINEs72heHIWlPZ8c6WY8MDU+Be5w1M+BK2kpcVhCUK\\nPJO4nMXpgamEX8DIiaO7emsunwJzMSvavSPRnxXXTKIc0i/g1EbiDjnYX9d85DkC\\nE1LaAUCmCZBVi9fIe0H2r9whIh4uLWZA41oMnJx/MOmo3XyMfQoWcqaSFlMqfZM4\\n0rNoB/tdHLNuV4eIdaw2mlHxdWDtF4oH+HFm+2cVBUVC1jXKrFv/euRVtsTT+A6i\\nh2XBHKxQ1Y4HgAn0jACP2QSPEmuoQEIa57bEKEcZsBR8SDY6ZdTd2HLRIApcCOSF\\nMRM8CKLeF658I0XgF8D5EsYoKPsA+74Z+jDH\\n-----END CERTIFICATE-----\\n-----BEGIN CERTIFICATE-----\\nMIIEBjCCAu6gAwIBAgIJAMc0ZzaSUK51MA0GCSqGSIb3DQEBCwUAMIGPMQswCQYD\\nVQQGEwJVUzEQMA4GA1UEBwwHU2VhdHRsZTETMBEGA1UECAwKV2FzaGluZ3RvbjEi\\nMCAGA1UECgwZQW1hem9uIFdlYiBTZXJ2aWNlcywgSW5jLjETMBEGA1UECwwKQW1h\\nem9uIFJEUzEgMB4GA1UEAwwXQW1hem9uIFJEUyBSb290IDIwMTkgQ0EwHhcNMTkw\\nODIyMTcwODUwWhcNMjQwODIyMTcwODUwWjCBjzELMAkGA1UEBhMCVVMxEDAOBgNV\\nBAcMB1NlYXR0bGUxEzARBgNVBAgMCldhc2hpbmd0b24xIjAgBgNVBAoMGUFtYXpv\\nbiBXZWIgU2VydmljZXMsIEluYy4xEzARBgNVBAsMCkFtYXpvbiBSRFMxIDAeBgNV\\nBAMMF0FtYXpvbiBSRFMgUm9vdCAyMDE5IENBMIIBIjANBgkqhkiG9w0BAQEFAAOC\\nAQ8AMIIBCgKCAQEArXnF/E6/Qh+ku3hQTSKPMhQQlCpoWvnIthzX6MK3p5a0eXKZ\\noWIjYcNNG6UwJjp4fUXl6glp53Jobn+tWNX88dNH2n8DVbppSwScVE2LpuL+94vY\\n0EYE/XxN7svKea8YvlrqkUBKyxLxTjh+U/KrGOaHxz9v0l6ZNlDbuaZw3qIWdD/I\\n6aNbGeRUVtpM6P+bWIoxVl/caQylQS6CEYUk+CpVyJSkopwJlzXT07tMoDL5WgX9\\nO08KVgDNz9qP/IGtAcRduRcNioH3E9v981QO1zt/Gpb2f8NqAjUUCUZzOnij6mx9\\nMcZ+9cWX88CRzR0vQODWuZscgI08NvM69Fn2SQIDAQABo2MwYTAOBgNVHQ8BAf8E\\nBAMCAQYwDwYDVR0TAQH/BAUwAwEB/zAdBgNVHQ4EFgQUc19g2LzLA5j0Kxc0LjZa\\npmD/vB8wHwYDVR0jBBgwFoAUc19g2LzLA5j0Kxc0LjZapmD/vB8wDQYJKoZIhvcN\\nAQELBQADggEBAHAG7WTmyjzPRIM85rVj+fWHsLIvqpw6DObIjMWokpliCeMINZFV\\nynfgBKsf1ExwbvJNzYFXW6dihnguDG9VMPpi2up/ctQTN8tm9nDKOy08uNZoofMc\\nNUZxKCEkVKZv+IL4oHoeayt8egtv3ujJM6V14AstMQ6SwvwvA93EP/Ug2e4WAXHu\\ncbI1NAbUgVDqp+DRdfvZkgYKryjTWd/0+1fS8X1bBZVWzl7eirNVnHbSH2ZDpNuY\\n0SBd8dj5F6ld3t58ydZbrTHze7JJOd8ijySAp4/kiu9UfZWuTPABzDa/DSdz9Dk/\\nzPW4CXXvhLmE02TA9/HeCw3KEHIwicNuEfw=\\n-----END CERTIFICATE-----\","
"    \"uri\": \"postgres://a03102bf6a63:b81da0190535@postgres-ba8904b8-bdeb-4268-9915-66c52ad76462.cqryblsdrbcs.us-east-1.rds.amazonaws.com:6275/wOPeoZIbVhnG\","
"    \"username\": \"a03102bf6a63\""
"  }"
"}"
```

#### Bind the service key to the application
```sh
$ cf bind-service cloudfoundry_circleci pg-instance-trial-key
```
[github circleci auth]: https://medium.com/@praveena.vennakula/github-circleci-authentication-ef1e85d24b0
[cloud foundry trial account]: https://developers.sap.com/tutorials/hcp-create-trial-account.html
[circle ci]: https://circleci.com/signup/

## Iage size
NOTE:
The total size of the Docker image file system layers must not exceed the disk quota for the app. The maximum disk allocation for apps is set by the Cloud Controller. The default maximum disk quota is 2048 MB per app.
### Cloud Foundry
Run arbitrary commands with a pushed apps with run-task

```sh
cf tasks Python_Bert
Getting tasks for app Python_Bert in org c44fa123trial / space dev as patrickdeutsch@gmail.com...

id   name       state       start time                      command
48   80f7e732   RUNNING     Mon, 15 May 2023 05:22:18 UTC   python opt/venv/cleaned_bert_similarity.py
47   30984d50   FAILED      Mon, 15 May 2023 03:23:03 UTC   python ops/venv/cleaned_bert_similarity.py
46   2b0a79d4   FAILED      Mon, 15 May 2023 03:07:57 UTC   python ops/venv/cleaned_bert_similarity.py
45   f138c2d5   FAILED      Sun, 14 May 2023 20:42:31 UTC   ls -la usr/local/
44   19856b6a   FAILED      Sun, 14 May 2023 20:41:53 UTC   ls -la /usr/local/
43   b0b5f720   SUCCEEDED   Sun, 14 May 2023 20:37:23 UTC   ls -la opt/venv/bin
42   ad0a2fc0   SUCCEEDED   Sun, 14 May 2023 20:36:36 UTC   ls -lah opt/venv/bin
41   fe88d718   SUCCEEDED   Sun, 14 May 2023 20:20:08 UTC   ls -lah opt/venv/bin
40   2561899a   SUCCEEDED   Sun, 14 May 2023 19:42:50 UTC   ls -lah opt/venv/bin
39   b124a776   SUCCEEDED   Sun, 14 May 2023 19:33:12 UTC   ls -lah opt/venv/bin
```
### fetch runtime logs 
```
$ cf logs Python_Bert --recent
Retrieving logs for app Python_Bert in org c44fa123trial / space dev as
...
   Collecting psycopg2-binary
   Downloading psycopg2_binary-2.9.6-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (3.0 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.0/3.0 MB 96.2 MB/s eta 0:00:00
   Collecting pandas
   Downloading pandas-2.0.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (12.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 12.3/12.3 MB 101.0 MB/s eta 0:00:00
   Collecting sentence-transformers
   Downloading sentence-transformers-2.2.2.tar.gz (85 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 86.0/86.0 kB 11.5 MB/s eta 0:00:00
   Preparing metadata (setup.py): started
   Preparing metadata (setup.py): finished with status 'done'
   Collecting joblib>=1.1.1
   Downloading joblib-1.2.0-py3-none-any.whl (297 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 298.0/298.0 kB 33.7 MB/s eta 0:00:00
   Collecting scipy>=1.3.2
   Downloading scipy-1.10.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (34.4 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 34.4/34.4 MB 54.3 MB/s eta 0:00:00
   Collecting threadpoolctl>=2.0.0
   Downloading threadpoolctl-3.1.0-py3-none-any.whl (14 kB)
   Collecting numpy>=1.17.3
   Downloading numpy-1.24.3-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (17.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 17.3/17.3 MB 77.9 MB/s eta 0:00:00
   Collecting pytz>=2020.1
   Downloading pytz-2023.3-py2.py3-none-any.whl (502 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 502.3/502.3 kB 46.0 MB/s eta 0:00:00
   Collecting python-dateutil>=2.8.2
   Downloading python_dateutil-2.8.2-py2.py3-none-any.whl (247 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 247.7/247.7 kB 33.5 MB/s eta 0:00:00
   Collecting tzdata>=2022.1
   Downloading tzdata-2023.3-py2.py3-none-any.whl (341 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 341.8/341.8 kB 38.9 MB/s eta 0:00:00
   Collecting transformers<5.0.0,>=4.6.0
   Downloading transformers-4.29.1-py3-none-any.whl (7.1 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 7.1/7.1 MB 110.3 MB/s eta 0:00:00
   Collecting tqdm
   Downloading tqdm-4.65.0-py3-none-any.whl (77 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 77.1/77.1 kB 15.7 MB/s eta 0:00:00
   Collecting torch>=1.6.0
   Downloading torch-2.0.1-cp310-cp310-manylinux1_x86_64.whl (619.9 MB)
   **ERROR** Could not install pip packages: could not run pip: signal: killed
   Failed to compile droplet: Failed to run all supply scripts: exit status 14
   Exit status 223 (out of memory)
   Cell e9aa27aa-5635-4e65-b14a-0ae5b04d7d5f stopping instance cb305155-1607-44ae-85b6-b6c1c768df36
   Cell e9aa27aa-5635-4e65-b14a-0ae5b04d7d5f destroying container for instance cb305155-1607-44ae-85b6-b6c1c768df36
StagingError - Staging error: staging failed
FAILED
```

### Docker image size
One was was to look for anything to chop out of the container image. The following command will list the top 10 largest files in the container image.  This is a good place to start looking for things to chop out of the container image.

```
du -amh / 2>/dev/null | sort -nr | head -n 10
```

here is what I came up with in the docker file after installing packages go clean up some junk
```dockerfile
rm -rf /root/.cache/pip && \
rm -rf /usr/local/lib/python3.9/distutils && \
rm -rf /usr/local/lib/python3.9/site-packages/pip/_vendor/ && \
find /opt/venv/ -type d \( -name 'tests' -o -name 'test' -o -name 'testing' \) -exec rm -rf {} + && \
find /opt/venv/ -type f \( -name '*_test.py' -o -name 'test.py' \) -delete
```

### Poetry
Went down a rabbit hole trying to use poetry in an attempt give more control with package installation 
but it was not worth the effort.  Poetry is a great tool but it is not a good fit for this project.

I like that poetry creates a virtual environment for the project and it is easy to install packages
also like that it creates a lock file to ensure that the same versions of packages are installed
there is the plugins like black that can be used to enforce code style. 

## BuildPacks
Pursued paketo buildpacks 
   really only has x86_64 support which makes a chicken and egg problem for building the buildpacks as running arm64 macos 
 it is possble but there was lengthy workaround documentation. 

 I really like that paketo can build an efficient container image with minimal effort.

# Container Vulnerabilties. 
gyrpe & sift are eazy to use locally, but challenges arise when trying to use the circleci orbs
snyk is a good option but requires a paid account to use in a CI pipeline.
trivy is a good option but requires a paid account to use in a CI pipeline.
need to explore clair more. 


## SPACY 
docker run -rm -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres


export VCAP_SERVICES='{"postgresql-db": [{"credentials": {"dbname": "postgres","hostname": "localhost","password": "postgres","port": "5432","username": "postgres","uri": "postgres://postgres:postgres@localhost:5432/postgres"}}]}'


FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints. check out the docs page

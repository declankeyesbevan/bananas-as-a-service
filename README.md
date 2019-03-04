# Bananas-as-a-Service

## About 
Bananas-as-a-Service is for the very common situation where you have a friend who has many
catch-phrases and you also have a team of software developers who work with him or her and who like
to be silly. That silly team likes to take the things that the friend says and re-form the words
into new, fun and silly sentences. For example, perhaps your friend likes to say "cool bananas" in
response to all new pieces of information on the progress of the project. Or maybe they are fond of
saying "five minutes" when asked how long any programming job will take. Maybe even they say
everything that takes "five minutes" will also be "easy". Everything that happens at work is "sick".
That silly team might think that from now on the latest JIRA story will be completed in "five sick
banana minutes". Maybe when they approve a pull request to show how much they find the code to be
solid, it could be rated as "five bananas" out of five. You know, normal things like that, that
normal people say and do. Normally.

These phrases will be crafted using the latest, greatest and matest so bleeding-edge it will make
your face bleed, Artificial Intelligence, Machine Learning, AI, ML, TLA, Buzzword, Acronym Goodness,
new-fangled and dangled technology Service-as-a-Service Driven Development. I would imagine.

### Disclaimer
Unless you work in this definitely fictional team you will most likely think this
software that I have lovingly crafted is total idiocy and that I should stop programming. I am fine
with that. Because this never happened.

## Requires

    python3.6

## Prerequisites
### Oxford Dictionaries API
An [Oxford Dictionaries API account](https://developer.oxforddictionaries.com). However this is only
required until this project is turned into a website in a 
[future release](#but-wait-theres-more-bananas). The `app_id` and `app_key` need to be stored in the
[AWS Parameter Store using Systems Manager](#systems-manager). 

### Environment Variables
You will need to set a number of environment variables. Examples can be found in 
[`.env.example`](.env.example). To export these to your BASH shell do the following:

    set -a
    . ./.env.example
    set +a

Creating a script for the above doesn't work because the setting and sourcing happens in a sub
shell. There are hacky ways around this but I try to avoid that where possible.

### AWS
You need to have an AWS account and it will need to be configured for
[CLI access](https://docs.aws.amazon.com/cli/latest/topic/config-vars.html) as the build/deployment
scripts require this.

#### Infrastructure
##### S3 and DynamoDB
These are created using CloudFormation. Execute 
[`scripts/deploy_infrastructure.sh`](scripts/deploy_infrastructure.sh) to create the stack. S3 is
used to store the packaged CloudFormation templates. The DynamoDB table is for storage and retrieval
of word metadata.  

#### Application
The Python application is packaged and deployed using the 
[AWS Serverless Application Model (SAM)](https://github.com/awslabs/serverless-application-model).

##### API Gateway
An API Gateway API accepts `POST` requests at the path `/banana` on the stage `api`.

##### Lambda
A Lambda function receives the API requests in the handler `app.lambda_handler`.

#### Identity Access Management
A policy of `AmazonDynamoDBFullAccess` is attached to this Lambda.

#### Systems Manager
To `GET` from the Oxford Dictionaries API an `app_id` and `app_key` are required. These are to be
kept in the
[AWS Systems Manager Parameter Store](
https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-paramstore.html) as
type `SecureString`. These can be added from environment variables to the Parameter Store using
[`scripts/store_secrets.sh`](scripts/store_secrets.sh).

#### Build
The SAM app can be built using [`scripts/build_app.sh`](scripts/build_app.sh).

#### Deploy
The SAM app can be deployed using [`scripts/deploy_app.sh`](scripts/deploy_app.sh).

#### SAM CLI
If you are debugging locally, you can use [AWS SAM CLI](https://github.com/awslabs/aws-sam-cli). You
can run [`scripts/start_sam_local.sh`](scripts/start_sam_local.sh) which starts the AWS
recommended Docker container and creates a local API Gateway at `http:localhost:3000/banana`. So far
I haven't been able to figure out how to get a nice remote debug session going on with sweet
breakpoints in PyCharm. Also to be able to send HTTP requests from Postman and actually have SAM CLI
respond I've had to tell SAM CLI to use a random debug port. This has been the biggest source of
frustration so far in this project. Setting breakpoints in local code and stepping through them on a
remote Docker host is usually quite simple to set up, but alas. Stay tuned. I have beer with which
to ponder this foe.

If you use multiple AWS accounts in your configuration and credential files, you will need to pass
the correct profile to SAM CLI. This is covered in the SAM local script with the environment
variable `AWS_PROFILE` falling back to `default` if not set.

## Installation

    git clone https://github.com/declankeyesbevan/bananas-as-a-service.git

## Usage
Bananas-as-a-Service in its current incarnation (v0.6) is a multi-threaded, object-oriented,
cloud storage backed, serverless, infrastructure-as-code version of the simple script from v0.1
where you send phrases and get back a bunch of sort of English sentences. See 
[`bananas_as_a_service/banana.py`](bananas_as_a_service/banana.py) for details.

### Command Line
You must put some phrases in a [file](tests/phrases.yml) and then pass it to the script via the
runner e.g.:

    python go_bananas.py --bananas phrases.yml

This runner simulates what API Gateway would pass to the triggered Lambda function so you can debug
the code locally.

You can also pass arguments to run a profiler on the application. This is:

    python go_bananas.py --bananas tests/performance/benchmark.yml --performance true

### HTTP
I use [Postman](https://www.getpostman.com) for manual testing locally or remotely. You can use it
with [SAM CLI](#sam-cli) to start a local API Gateway and Lambda; or after deployment to AWS.

## But wait, there's more bananas
I originally started this as a joke because I thought it would be fun to make some sentences out of
my friend's phrases like we do in real life (you know who you are, person who started this). Then I
realised that Natural Language Processing takes more than three beers and a few hours of Python. So
for v0.1 I wrote some code than does the silly then decided it would be cool and fun to actually
showcase my (limited) skill-set and turn this into a portfolio piece. Which roughly means future
versions will roll out with these upgrades:

- ~~Object Oriented (FTW)~~ `v0.2`
- ~~Multi-threading (Parallel, whoo)~~ `v0.3`
- ~~Storage (DynamoDB)~~ `v0.4`
- ~~Serverless (AWS Serverless Application Model)~~ `v0.5`
- ~~CI/CD (AWS CodePipeline and Friends)~~ `v0.6`
- Testing (Pytest and Martin Fowler's Testing Pyramid)
- API (Who gots the Swagger)
- Automation (Ansible)
- Caching (Elasticache/Redis)
- Front-end (React.js)
- Documentation (Sphinx)
- Monitoring (CloudWatch/ELK)
- Voice in (Amazon Transcribe)
- Voice out (Amazon Polly)
- Adding some actual smarts to the sentence construction using Natural Language Processing
- Becoming Certified Buzzword Compliant (ISO-35000)

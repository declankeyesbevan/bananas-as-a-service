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
your face bleed, Aritifical Intelligence, Machine Learning, AI, ML, TLA, Buzzword, Acronym Goodness,
new-fangled and dangled technology Service-as-a-Service Driven Development. I would imagine.

### Disclaimer
Unless you work in this definitely fictional team you will most likely think this
software that I have lovingly crafted is total idiocy and that I should stop programming. I am fine
with that. Because this never happened.

## Installation

    git clone https://github.com/declankeyesbevan/bananas-as-a-service.git

## Pre-requisites
An [Oxford Dictionaries API account](https://developer.oxforddictionaries.com). However this is only
required until this project is turned into a website in a 
[future release](#but-wait-theres-more-bananas). You will need to set two environment variables for 
the API key credentials:

    APP_ID
    APP_KEY

## Requires

    python3.6

## Usage
Bananas-as-a-Service in its current incarnation (v0.2) is an object-oriented version of the simple
script from v0.1 where you pass a YAML file of phrases and get back a bunch of sort of English
sentences thrown to the logger. See 
[`bananas_as_a_service/banana.py`](bananas_as_a_service/banana.py)
for details but essentially you put some phrases in a [file](tests/phrases.yml) and then pass it to 
the script via the runner e.g.:

    python go_bananas.py --bananas phrases.yml

## But wait, there's more bananas
I originally started this as a joke because I thought it would be fun to make some sentences out of
my friend's phrases like we do in real life (you know who you are, person who started this). Then I
realised that Natural Language Processing takes more than three beers and a few hours of Python. So
for v0.1 I wrote some code than does the silly then decided it would be cool and fun to actually
showcase my (limited) skill-set and turn this into a portfolio piece. Which roughly means future
versions will roll out with these upgrades:

- ~~Object Oriented (FTW)~~ `v0.2`
- Multi-threading (Parallel, whoo)
- Storage (DynamoDB)
- Caching (Elasticache/Redis)
- Serverless (AWS Serverless Application Model)
- CI/CD (AWS CodePipeline and Friends)
- Testing (Pytest and Martin Fowler's Testing Pyramid)
- API (Who gots the Swagger)
- Front-end (React.js)
- Documentation (Sphinx)
- Monitoring (CloudWatch/ELK)
- Voice in (Amazon Transcribe)
- Voice out (Amazon Polly)
- Adding some actual smarts to the sentence construction using Natural Language Processing
- Becoming Certified Buzzword Compliant (ISO-35000)

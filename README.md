# Chatapp-serverless

Latest API generated: 
https://p5iwu324m5.execute-api.eu-west-1.amazonaws.com/Prod/login

This is a serverless chat-application that works mostly as a proof of concept for creating a webserver with all it's routes be hosted as serverless instead of having a server idly running.  

To use the SAM CLI in this project, you need the following tools.

- SAM CLI (With AWS CLI) - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
- [Python 3.12 installed](https://www.python.org/downloads/)
- Docker - [Install Docker community edition](https://hub.docker.com/)

## Build

To build and test your application for the first time, run the following in your shell (env variable needs to have MongoDB_URI pointing to a mongodb cluster and SECRET_KEY needs to be a secret key for access token creation):

```bash
sam build --use-container
```

To run it locally run the following command

## Deploy

### Local

```bash
sam local start-api --env-vars env.json
```

### Prod

To Deploy it run the following command

```bash
sam deploy --guided
```

**Important** AWS needs to have your MongoDB_URI set on AWS SSM by running the commands

```bash
aws ssm put-parameter --name "Parameter_MONGODB_URL" --value "<MONGO_DB_URL>" --type "String" --overwrite
```

```bash
aws ssm put-parameter --name "Parameter_SECRET_KEY" --value "<SECRET_KEY>" --type "String" --overwrite
```

## Cleanup

To take down the serverless application from AWS, run the following code in the terminal that you deployed

```bash
sam delete
```

# AWS Bedrock Workshop Setup Guide

This workshop guides you through setting up and using Amazon Bedrock with LLama models. Follow these steps carefully to ensure proper configuration of your environment.


## Workshop Access

1. Access the workshop using [this link](https://catalog.us-east-1.prod.workshops.aws/join?access-code=e9bf-0c510a-75)
2. Enter your email address to receive the passcode
3. Input the received passcode to gain access

## Setup Steps

### 1. Enable Bedrock Model Access

1. Navigate to the Bedrock console
2. Click on "Enable Bedrock Model Access"
3. Select "Enable All Models"
4. Click "Next"
5. Click "Submit"

Note: You may encounter some errors during this process - these can be safely ignored.

### 2. IAM Role Configuration

#### Create EC2 IAM Role

1. Go to the IAM Console
2. Navigate to "Roles" in the left sidebar
3. Click "Create new role"
4. Keep "AWS Service" as the default Trusted entity Type
5. Select "EC2" from the "Use Case" dropdown
6. Click "Next"
7. Search for and select "AdministratorAccess"
   > ⚠️ Note: This is not a security best practice and should only be used for workshop purposes
8. Click "Next"
9. Provide a role name
10. Click "Create Role"

#### Modify WSParticipantRole

1. In IAM Roles, select "WSParticipantRole"
2. Select "iam_policy-0" and edit the policy
3. Around line 154, remove the explicit denies for the meta llama models
4. Save the policy

### 3. Cloud9 Environment Setup

1. Navigate to the Cloud9 Console
2. Click "Create Environment"
3. Configure the environment:
   - Provide a name
   - Keep "New EC2 Instance" as environment type
   - Select t3.small instance type
   - Leave other settings as default
4. Click "Create"
5. Once ready, click "Open"

### 4. Assign IAM Role to Cloud9

1. Go to EC2 console
2. Navigate to "Instances (running)"
3. Select the running instance
4. Choose Actions → Security → Modify IAM Role
5. Select the previously created IAM role from the dropdown

### 5. S3 Bucket Creation

1. Navigate to S3 Console
2. Click "Create Bucket"
3. Provide a globally unique name (save this for Lab2)
4. Keep default settings
5. Click "Create Bucket"

### 6. Workshop Environment Setup

1. Return to Cloud9 console and click "Open"
2. In the terminal, clone the repository:
```bash
git clone https://github.com/dbavro19/llama-tool-use.git
```

3. Install requirements:
```bash
pip install -r requirements.txt
```

4. Navigate to project directory:
```bash
cd llama-tool-use/
```
and Start the Application
```bash
streamlit run statuscheck.py --server.port 8080 --server.enableXsrfProtection=False
```

5. Preview the running application in Cloud9

## Additional Resources

- [Workshop Repository](https://github.com/dbavro19/llama-tool-use)
- [AWS Workshop Environment](https://catalog.us-east-1.prod.workshops.aws/join?access-code=e9bf-0c510a-75)

## Support

If you encounter any issues during setup, please refer to the workshop facilitators or raise an issue in the GitHub repository.

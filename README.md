![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Rag](https://img.shields.io/badge/Rag-FF4B4B?style=for-the-badge&logo=rag&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![EC2](https://img.shields.io/badge/EC2-FF9900?style=for-the-badge&logo=aws&logoColor=white)
![Bedrock](https://img.shields.io/badge/Bedrock-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Elastic](https://img.shields.io/badge/Elasticsearch-005571?style=for-the-badge&logo=elasticsearch&logoColor=white)

# Exploring the AWS Bedrock Knowledge Bases. 
```mermaid
graph TD
    subgraph DataSources
        A[S3]
        B[Web Crawler]
        C[Confluence]
        D[Sharepoint]
        E[Salesforce]
    end
    A --> F
    B --> F
    C --> F
    D --> F
    E --> F
    F[Knowledge Base] --> G
    G[OpenSearch Vector Store]
```
# Combined OpenSearch Vector Store
As the OpenSearch Vector Store is the costly component of the architecture. I created a combined OpenSearch Vector Store 
at the time of retrieval we pass in filters so we can retrieve only the relevant data. This way we can reduce the cost of
the OpenSearch Vector Store. When you create a OpenSearch Vector Store it reserves the resources, and you can not turn it off.
```mermaid
flowchart
    C[Web Crawler: SUM SUM] --> F
    D[Web Crawler: Cronos] --> F
    F[KB: SUMSUM] --> G
    G[Combined OpenSearch Vector Store]

    H[S3: Raccoons Flyers] --> J
    I[S3: Raccoons Docs] --> J
    J[KB: Raccoons] --> G
```

# Project structure
```
.
├── app.py  # Streamlit app
├── config.py  
├── create_url.py  # tool to create access url for knowledge base
├── private_key.pem  # create your own private key
├── public_key.pem  # with a match public key
├── README.md
├── requirements.txt
└── utils.py  # helper functions
```
# Installation on EC2
## Clone the repository
```bash
git clone https://github.com/GerritGeeraerts/aws-kb-demo
cd ./aws-kb-demo
```
## Creating public and private key for secure access links
```bash
openssl genpkey -algorithm RSA -out private_key.pem -pkeyopt rsa_keygen_bits:768
openssl rsa -pubout -in private_key.pem -out public_key.pem
```
## Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Manually test the project
```bash
streamlit run app.py
```

## Automatically start app on startup
### Create the service file
```bash
sudo nano /etc/systemd/system/streamlit-app.service
```
Copy the code below and paste it in the file, make sure to replace the placeholders:
* Replace ***USERNAME*** with your username (use `whoami` to get your username)
* Replace ***PATH_TO_YOUR_PROJECT***
* Replace ***PATH_TO_YOUR_VENV***
```ini
[Unit]
Description=Streamlit App Server

[Service]
User=***USERNAME***
WorkingDirectory=/***PATH_TO_YOUR_PROJECT***
ExecStart=/***PATH_TO_YOUR_VENV***/bin/streamlit run app.py
Restart=always

[Install]
WantedBy=multi-user.target
```
### Enable the service
```bash
sudo systemctl enable streamlit-app.service
```
### Start the service
```bash
sudo systemctl start streamlit-app.service
```
### Verify the service
```bash
sudo systemctl status streamlit-app.service
```
# Requirements
The EC2 need a role that has a policy with the following permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:ListDataSources",
                "bedrock:RetrieveAndGenerate",
                "bedrock:Retrieve",
                "bedrock:InvokeModel"
            ],
            "Resource": "*"
        }
    ]
}
```
# Create access url for knowledge base
The app can talk with different AWS Bedrock Knowledge Bases. To talk to a specific knowledge base, you need to create 
an encrypted URL. You can do this with the `create_url.py` script. The encrypted url serves as
you have access only if you know the url. So you can easily share secure urls without managing logins.
Run the script and provide the knowledge base id when prompted.
```bash
python create_url.py
```
The script will output an encrypted URL that serves as you can only access the demo if you have the url. Make sure to 
replace `localhost` with the public ip of your ec2.


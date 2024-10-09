- # AWS Bedrock Knowledge Bases
- ## Explore
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
    - ### Data Sources Layer
        - Data sources hold configuration to access data, so when you create a web crawler for example nothing is crawled yet.
    - ### Opensearch Vector Store
        - This is the vector store which is derived from elastic search.
        - In the dashboard you can execute DSL (Elastic search) query's
    - ### Knowledge base Layer
        - Is responsible for getting the data from the Data Sources to the vector store. This happens when you Sync. In the case of a web crawler it will start when you hit sync.
- ## Applied Example: Out of the Box
    ```mermaid
    flowchart 
      C[Web Crawler: SUM SUM] --> F
      D[Web Crawler: Cronos] --> F
      F[KB: SUMSUM] --> G
      G[$ OpenSearch Vector Store]
      
      H[S3: Raccoons Flyers] --> J
      I[S3: Raccoons Docs] --> J
      J[KB: Raccoons] --> K
      K[$ OpenSearch Vector Store]
    ```
- ## Applied Example: Combined Vector store
    ```mermaid
    flowchart
      C[Web Crawler: SUM SUM] --> F
      D[Web Crawler: Cronos] --> F
      F[KB: SUMSUM] --> G
      G[$ Combined OpenSearch Vector Store]
      
      H[S3: Raccoons Flyers] --> J
      I[S3: Raccoons Docs] --> J
      J[KB: Raccoons] --> G
    ```
    - ### Generating and retrieving with KB's
        - I will be using [RetrieveAndGenerate](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_RetrieveAndGenerate.html) but you can also seperatly [Retrieve](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_Retrieve.html) and generate with [InvokeModel](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModel.html)
        - #### Configuration: Guardrails
            - (Example: "Do not answer generic prompts, only answer data about SUMSUM company")
        - #### Configuration: Prompt Templates
            - Set a custom system message
        - #### Configuration: knowledgeBaseId
            - You can specify the KB-ID but this is confusing:
              When making a chat completion request you need to provide a `knowledgeBaseId`,   
              but its actually is talking to the vector store attached to it. So when you make   
              a chatcompletion request to the `SumsumKnowledgeBaseId` you will be chatting with   
              `Combined OpenSearch Vector Store` and therefor with `KB: SUMSUM` and `KB: Raccoons`  
        - #### Configuration: Retrieval filters
            - With filters, we can solve the problem of above, via the `ListDataSources` we can list the all the data 
            - sources used in for example the SUMSUM KB and then we can build a filter like this:
            -
              ```json
              {
                "filter": {
                  "orAll": {
                    "equals": {
                      "key": "x-amz-bedrock-kb-data-source-id",
                      "value": "kb_sumsum_webcrawler_datasource_id"
                    },
                    "equals": {
                      "key": "x-amz-bedrock-kb-data-source-id",
                      "value": "kb_sumsum_s3_datasource_id"
                    }
                  }
                }
              }
              ```
            - Like this we can chat with only the sumsum data and not with the raccoons data
            - There is a METADATA field on vectorstore, this field is stringified json. I was unable to filter on this data. Some other fields where not indexed and i was also unablet to filter on them.
  - ## Conclusion
      - 🟢 **Data sources are superfast added** to a knowledge base if they are in one of the provided formats.
      - 🟢 Its super easy to (re)crawl a website or any datasource via the **easy sync option**.
      - 🟢 Easy button that can split query into sub queries to get a better retrieval results
      - 🟢 Hybrid search (keyword and vector)
      - 🟢 Contextualizes rag queries out of the box
      - 🟢 Agent based retrieval for multiple retrieval calls.
      - 🟢 A lot is abstracted away what makes it easy to use.
      - 🔴 A lot is abstracted away, you can not see or change what's happening under the hood.
      - 🔴 Bedrock Knowledge bases has a lot of **preview** features and is a product that is actively being worked on.
      - 🔴 I miss a way to turn of the opensearch service, or to pay per retrieval request, the open search vector store locks resources even if you do not search. from my actual costs used I estimate it at about minimal **130$ per month per open search vector db**.
      - 🔴 **I miss** a simple way to chat with **multiple databases on 1 vector store**, needs some configurations and workarounds to setup.
      - 🔴 The web crawler does not handle images, I do think it handles pdf files it finds (not tested).
      - 🔴 **AWS documentation could be better.** Some vital info is not found in the official docs like how to configure the filters or what language is used to filter.
      - 🔴 boto3 is python library to interact with the aws services. It is the only python library that I know of that loads its functions at runtime. This means no autocomplete, and constant alt tabbing to the browser to find the name of a function or argument. This in the age where copilots are developed to be hyper friendly for developers and which are basically autocomplete on steroids.
- # Streamlit
	- Its popular in the data world as you do not need to be a webdev and it handles data visualizations well.
	- 🟢 A python only web dev tool. No need to write html or javascript. When used for simple apps very easy and fast to develop.
	- 🔴 Bigger more complex apps it becomes a mess as it is encouraged to work with session vars and the more session vars you have the more states your app can be which can become very complex very quickly to keep track.
	- 🔴 Challenging to host on lambda, as lambda requests need to be mapped to the tornado server. This is possible with a custom handler function or using docker and [aws-lambda-web-adapter:(https://github.com/awslabs/aws-lambda-web-adapter)
	- Fun Link: [Pure Python Web Application Development – NO CSS, HTML, or Javascript needed](https://www.may69.com/purepython/#Requirements_of_a_Class_A_System)
- # Firecrawl
	- Is an easy to use web crawler, given a base url it completly crawls a website, converts to markdown, collects metadata, has some auto configs that can be overided to exclude headers, footers, etc.
	- 🟢 Open source
	- 🟢 Self hosted or as a service
	- 🟢 Has a Langchain integration
	- 🔴 Self host is challenging
- # Langsmith
	- 🟢 LLM Telemetry, easy to monitor production LLM applications, very detailed, for every step that is made by
	- 🟢 You can also collect user feedback.
- # Langchain
	- ## Contextulazing rag queries
		- Reformulating a prompt together with the chat history to have a better prompt for retrieving information. (In amazon i have the feel that this is out of the box)
	- ## Agent based retrieval
		- Via working with an agent letting the agent decide how many calls are made for retrieval. (in amazon this is the split query button)
	- # Conclusion
		- 🟢 Full Control over everything for example: Control over doc similarity
		- 🟢 Extensible plugins: integrate all kind of models / tools
		- 🟢 It also integrates with Amazon services
		- 🟢 Flexibility
		- 🔴 Complex
- # LLM
	- ## Chunk sizes
		- Too small chunk sizes can lose context of information. For example the ppl that where working at sumsum question. Was never going to be able to answer it because the people names got seperated by the working at sumsum context.
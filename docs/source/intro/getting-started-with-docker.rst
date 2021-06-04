.. _CKG Docker Container:


CKG Docker Container
============================================

In this section we describe how to set up the Clinical Knowledge Graph from a Docker container.
This container will install all the requirements needed, download source databases and build the CKG graph database, and open 5 ports through which to interact with the CKG.

To run the Docker, simply:

1. Clone CKG’s repository: https://github.com/MannLabs/CKG

2. Get licensed databases: https://ckg.readthedocs.io/en/latest/intro/getting-started-with-build.html#build-neo4j-graph-database

3. Download the database dump and data directory from Mendeley:
            https://data.mendeley.com/public-files/datasets/mrcf7f4tc2/files/
	    
4. Extract compressed data file into the CKG folder and copy licensed databases in the right directories: 

- data/databases/{DrugBank|PhosphoSitePlus}

- data/ontologies/SNOMED-CT

5. Move the dump file to CKG/resources/neo4j_db

6. Build  thecontainer: 

.. code-block:: bash
	
	$ cd CKG/
	$ docker build -t docker-ckg:latest .

7. Run docker:

.. code-block:: bash

	$ docker run -d --name ckgapp -p 7474:7474 -p 7687:7687 -p 8090:8090 -p 8050:8050 -v local_neo4j_logs_path:/var/log/neo4j -v local_ckg_directory_path:/CKG docker-ckg:latest


**local_neo4j_logs_path**: path where you want to store the neo4j logs

**local_ckg_directory_path**: path where CKG is installed

Once the docker is running:

1. Access JupyterHub: http://localhost:8090/:

- user:ckguser

- password:ckguser

2. Access Neo4j browser (connection may take several minutes): http://localhost:7474/

3. Login using: 

- user: neo4j

- password: NeO4J

When the database is running:

1. In your web browser access CKG app: http://localhost:8050/
2. Login using the test user:

- user: test_user

- password: test_user
  
3. In the Home page navigate to the Admin page

4. Run Minimal update (these can take a while but will run in the background. Follow progress in the docker dashboard logs)

5. Explore options in CKG


.. note:: Be aware, this requires Docker to be previously installed.

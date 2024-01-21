# Educational Project for BoilerMake 2024

### Inspiration: 
We have all participated in some form of teaching, whether it be tutoring, volunteering, helping out during office hours and PSOs as a TA, even simply explaining a problem to our friends. In our various experiences relating concepts in simpler terms, we've noticed that explaining and learning is often easier done visually. However, when attempting to formulate a math problem into an image can be difficult at first, particularly for younger students who are just beginning to learn the entire new language that is mathematics. We wanted to create a platform to help stimulate visual imagination (or, iMaiTHination ;) ) for math problems, to not only provide an entertaining boost for the present math, but to also cultivate the connection between symbols on paper and what we see through our own eyes. Additionally, our web application would be helpful for children whose second language is English and struggle to get past any language barrier when learning math. 

### Description
Our application can be split into three parts: reading in data, processing, and generating the image. We allow the user the option to either type in their word problem, or upload a file of the problem. Once the user inputs their data in the desired format, our application will parse the data, and then display an image corresponding to their math word problem. 

### Setting up the virtual environment: 
#### On mac: 

```bash
python -m venv env
source env/bin/activate
```

#### On windows: 

```bash
python -m venv env
.\env\Scripts\activate
```

### Make sure you have the required packages listed on *requirements.txt* downloaded, then run: 

```bash 
flask app --app run
```


# battlesnake-python (Name TBA)

## Ethan Wipond and Wyll Brimacombe

Fork of [battlesnake-python](https://github.com/sendwithus/battlesnake).

Master branch is auto-deployed to https://era-snake.herokuapp.com/

This AI client uses the [bottle web framework](http://bottlepy.org/docs/dev/index.html) to serve requests and the [gunicorn web server](http://gunicorn.org/) for running bottle on Heroku. Dependencies are listed in [requirements.txt](requirements.txt).

## Running the Snake Locally

1) Clone repo to your development environment:
```
git clone git@github.com:username/battlesnake-python.git
```

2) Install dependencies using [pip](https://pip.pypa.io/en/latest/installing.html):
```
pip install -r requirements.txt
```

3) Run local server:
```
python app/main.py
```

4) Test client in your browser: [http://localhost:8080](http://localhost:8080).

5) Start the test server
```
sudo docker run -it --rm -p 3000:3000 sendwithus/battlesnake-server
```


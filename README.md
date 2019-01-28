# battlesnake-python (Crayon)

## Ethan Wipond and Wyll Brimacombe

Fork of [battlesnake-python](https://github.com/sendwithus/battlesnake).

Master branch is auto-deployed to https://era-snake.herokuapp.com/

This AI client uses the [bottle web framework](http://bottlepy.org/docs/dev/index.html) to serve requests and the [gunicorn web server](http://gunicorn.org/) for running bottle on Heroku. Dependencies are listed in [requirements.txt](requirements.txt).

2019 documentation is here: [http://docs.battlesnake.io/](http://docs.battlesnake.io/)

2018:
Beat Semaphore, Giftbit, Redbrick, and Bambora.

2019: 
???

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

5) Start the [test server](http://docs.battlesnake.io/zero-to-snake-linux.html)

```
cd battlesnake-engine
./engine-dev
```

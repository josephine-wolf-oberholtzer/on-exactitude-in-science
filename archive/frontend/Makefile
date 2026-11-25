imageName = josiahwolfoberholtzer/on-exactitude-in-science-gui
gitCommit = git rev-parse HEAD

build:
	docker build -t ${imageName}:latest .
	docker build -t ${imageName}:${gitCommit} .

push: build
	docker login -u josiahwolfoberholtzer
	docker push ${imageName}:latest
	docker push ${imageName}:${gitCommit}

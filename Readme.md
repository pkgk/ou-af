20 Augustus start ontwikkelen in macos

DEVCONTAINERS
- devcontainers, er zijn blijkbaar meerdere mogelijkheden
- devcontainer.json file stuurt het geheel, Dockerfile is er om container te maken

1. zelf .devcontainer dir aanmaken en die dan in vscode met "reopen" starten 
- nadeel is dat bestanden op schijf blijven staan

2. new devcontainer aanmaken via vscode "new devcontainer"
- nadeel daarna git initialiseren en met github linken

3. devcontainer obv cloned repository
- meteen aan git gelinkt

DOCKERFILES
#buildx commando's
# create a build: 
docker buildx create --name OUAF --use

# build, let op punt aan het einde
docker buildx build --push --tag peterkoenkoning/ouaf:buildx-latest --platform linux/arm64 .
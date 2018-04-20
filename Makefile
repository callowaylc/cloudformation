export ORG ?= callowaylc
export PROJECT ?= cloudformation
export AWS_DEFAULT_REGION ?= us-east-1
export WORKDIR ?= /opt/bin
export PATH_PROFILES ?= "./profiles"
export PATH_TEMPLATES ?= "./templates"
ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))

-include Makefile.functions

.PHONY: dependencies assume login build test deploy push bootstrap orchestrate clean

dependencies:
	mkdir -p ./build

## orchestration workflow #######################

assume:
	$(call assume_role,cloudformation)

login: assume
	@ eval `aws ecr get-login --no-include-email --region $(AWS_DEFAULT_REGION)`

build:
	$(call assume_role,admin)
	@ docker-compose build --force-rm base
	@ docker-compose run --rm install
	@ docker-compose build --force-rm main

test: assume
	@ docker-compose run --rm test

tag: assume
	docker tag $(ORG)/$(PROJECT) $(AWS_DOCKER_REGISTRY)/$(ORG)/$(PROJECT):latest
	docker tag $(ORG)/$(PROJECT) $(AWS_DOCKER_REGISTRY)/$(ORG)/$(PROJECT):`git rev-parse --short HEAD`

push: assume
	@ docker push $(AWS_DOCKER_REGISTRY)/$(ORG)/$(PROJECT)

publish: assume
	@ docker-compose run --rm base \
			aws s3 cp \
				--recursive \
				--exclude="*" \
				--include="*.yaml" \
					./templates s3://$(AWS_CLOUDFORMATION_BUCKET_NAME)

## developer workflow ###########################

install:
	ln -fs `pwd`/bin/cloudformation.sh /usr/local/bin/cloudformation

bootstrap:
	$(call assume_role,admin)
	@ ./bin/cloudformation.sh --loglevel INFO --profile bootstrap.yaml \
		cloudformation \
			--disable-rollback \
			--capabilities \
			--disable-bucket \

orchestrate: assume
	$(call assume_role,cloudformation)
	@ ./bin/cloudformation.sh --loglevel INFO --profile $(ARGS) \
		cloudformation \
			--disable-rollback \
			--capabilities \
			--disable-bucket

clean:
	docker-compose down --remove-orphans -v --rmi local
	- docker rmi -f $$(docker images --filter "label=project=$(PROJECT)" -q)
	- docker rmi -f $$(docker images --quiet --filter "dangling=true")
	rm -rf ./build

%:
	@:

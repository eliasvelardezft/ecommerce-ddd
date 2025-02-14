.PHONY: start
start:
	docker run -d -p 27017:27017 --name mongodb mongo:latest || true  # || true prevents error if container exists
	uvicorn src.main:app --reload --host 0.0.0.0 --port 9000

.PHONY: stop
stop:
	docker stop mongodb || true
	docker rm mongodb || true

.PHONY: clean
clean:
	docker stop mongodb || true
	docker rm mongodb || true
	docker rmi mongo:latest || true
	docker volume rm mongodb_data || true
	docker network rm mongodb_network || true
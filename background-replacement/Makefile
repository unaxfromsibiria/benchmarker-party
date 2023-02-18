
benchmark:
	$(MAKE) benchmark_pypy
	@echo "C implementation with CFFI:"
	python -m bg_replacer.run  --repeat "$(count)" --impl cffi
	@echo "C implementation with Cython:"
	python -m bg_replacer.run  --repeat "$(count)" --impl cython

benchmark_pypy:
	@echo "Implementation with using Numpy:"
	python -m bg_replacer.run  --repeat "$(count)" --impl numpy
	@echo "Implementation with using native Python with Numpy structures:"
	python -m bg_replacer.run  --repeat "$(count)" --impl "np+py"

benchmark_numba:
	@echo "Implementation with using Numba & Numpy:"
	python -m bg_replacer.run  --repeat "$(count)" --impl "numba+np"
	@echo "Implementation with using Numba & Python structures:"
	python -m bg_replacer.run  --repeat "$(count)" --impl numba

benchmark_all:
	$(MAKE) benchmark
	$(MAKE) benchmark_numba

in_python311:
	@echo "Building container from python:3.11-slim-buster"
	docker build -f py311.Dockerfile -t bg-replacer-py-311 .
	docker run -it bg-replacer-py-311

in_python310:
	@echo "Building container from python:3.10-slim-buster"
	docker build -f py310.Dockerfile -t bg-replacer-py-310 .
	docker run -it bg-replacer-py-310

in_pypy:
	@echo "Building container from pypy:3.9-slim-bullseye"
	docker build -f pypy.Dockerfile -t bg-replacer-pypy .
	docker run -it bg-replacer-pypy

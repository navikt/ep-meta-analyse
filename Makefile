.PHONY: $(shell sed -n -e '/^$$/ { n ; /^[^ .\#][^ ]*:/ { s/:.*$$// ; p ; } ; }' $(MAKEFILE_LIST))

this_dir := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

help:
	 @echo "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/\\x1b[36m\1\\x1b[m:\2/' | column -c2 -t -s :)"

python-bootstrap: # Setter opp miljø for analyse
	brew install cloc
	git config --global core.quotepath off # fikser issue med UTF-8 i filnavn https://github.com/AlDanial/cloc/issues/457
	brew install poetry
	poetry install
	@make jupyter-output-filter-install

jupyter-output-filter-install: # Installerer et git-filter som fjerner output i notebook'er så det ikke sjekkes inn
	brew install jq
	git config --local filter.jupyter-remove-output.clean "(cat %f | jq '.cells[] |= if has(\"execution_count\") then .execution_count = null else . end' | jq 'del(.cells[].outputs[]?)' | jq 'del(.cells[].metadata[]?)')"
	git config --local filter.jupyter-remove-output.smudge "cat"

analyse-and-update-notebook: python-bootstrap
	poetry run jupyter nbconvert --execute --to notebook --inplace "Utviklingsstatistikk.ipynb"

generate-notebook-pdf: analyse-and-update-notebook ## Generer Utviklingsstatistikk.pdf fra Utviklingsstatistikk.ipynb
	poetry run jupyter nbconvert "Utviklingsstatistikk.ipynb" --output "output/Utviklingsstatistikk" --to webpdf --TemplateExporter.exclude_input=True --allow-chromium-download

# Statistikk fra EESSI-PENSJON

### Installer nødvendige biblioteker 
```
brew install cloc
brew install python@3.11

```

## For å hente ut info om siste ukes commits
```
./scripts/commit-stats-py
```
Resultatet vil kan da hentes i analyse/commit-stats.csv

## Dokumentasjon

## Henvendelser

Spørsmål knyttet til koden eller prosjektet kan rettes mot:

* Mariam (mariam.pervez at nav.no)

## Feilmeldinger
### Feil python versjon; bruk 3.11 eller høyere
```
Traceback (most recent call last):
  File "./script/commit-stats.py", line 5, in <module>
    from zoneinfo import ZoneInfo
```


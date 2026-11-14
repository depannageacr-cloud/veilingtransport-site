# Veilingtransport by ACR

Website voor aanvragen voor transport van veilingaankopen. De homepage is uitgebreid met 40 inhoudelijk verschillende gidsen, informatie over ACR en een invulbare afhaalchecklist.

## Onderhoud

Bewerk `_source/content.py` voor de 40 gidsen. De oorspronkelijke homepage staat in `_source/homepage-source.html`.

Opnieuw bouwen en controleren, met alleen de Python- en Node-standaardbibliotheek:

```
python _source/build.py
python _source/verify.py
node _source/test-checklist.cjs
```

De bronmap wordt via Apache geblokkeerd voor directe HTTP-toegang. De bron is wel openbaar in deze GitHub-repository.

## Publicatie

OVH: hosting `gxmvgeh.cluster130.hosting.ovh.net`, websitemap `veilingtransport`, repositorybranch `main`. Bevestig na iedere uitrol de geslaagde deployment en controleer pagina’s en `sitemap.xml` live.

De sitemap bevat 41 canonieke pagina-adressen. `llms.txt` en `ai-info.json` zijn aanvullende feiten- en verwijsoverzichten. Ze garanderen geen indexering, zoekpositie of AI-vermelding.

De checklist slaat geen gegevens op en verstuurt geen aanvragen op de achtergrond. Contact wordt door de bezoeker zelf verstuurd via WhatsApp, e-mail of het centrale ACR-formulier.

## Laatste controle

14 november 2026: alle lokale bestemmingen en ankers, 41 unieke titels en beschrijvingen, canonicals, JSON-LD, sitemap en checklistgedrag gecontroleerd. Een mobiele/desktopbrowsercontrole kon in deze uitvoeromgeving niet worden voltooid. Controleer de laatste live uitrol afzonderlijk.

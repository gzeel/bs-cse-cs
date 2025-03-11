# Cloud Automation: De Reis naar DevSecOps via De Drie Wegen

## Casus Achtergrond

Ahumbo, een grote Nederlandse supermarktketen, is in een digitale crisis beland. Het bedrijf heeft de afgelopen jaren fors geïnvesteerd in een online bestelsysteem en bezorgservice om te concurreren met pure e-commerce spelers. Aanvankelijk draaiden deze systemen op lokale servers in hun eigen datacenter, maar twee jaar geleden nam het management een strategisch besluit: Ahumbo moest "naar de cloud".

Onder druk van consultants en met de belofte van flexibiliteit en kostenbesparingen werden vrijwel alle workloads naar Azure gemigreerd - maar via een klassieke "lift and shift" aanpak. De Java-applicaties draaien nu op tientallen virtuele machines in Azure, maar de architectuur is nog steeds monolithisch. Niemand heeft een volledig overzicht van hoe alles samenhangt. De codebase doet denken aan een archeologische opgraving - lagen op lagen code, waar niemand meer aan durft te komen uit angst dat het hele systeem instort.

In de directiekamer wordt de spanning voelbaar wanneer de CFO, Maria Gonzalez, het kwartaalrapport presenteert. "Onze Azure-kosten zijn het afgelopen jaar met 230% gestegen," zegt ze met een diepe frons. "De beloofde kostenbesparingen zijn niet gerealiseerd - integendeel. We betalen nu meer dan ooit, en niemand lijkt te kunnen uitleggen waarom."

De CEO, Pieter van den Berg, slaat met zijn vlakke hand op de vergadertafel. "Ik krijg dagelijks klachten van klanten die hun boodschappen niet kunnen bestellen. Onze bezorgers staan soms voor een gesloten deur omdat bestellingen verkeerd zijn verwerkt. Dit kost ons niet alleen klanten, maar ook onze reputatie!"

"En dat is nog niet alles," voegt Jan-Willem de Groot, de CIO, toe. "Er is niemand die echt de eigenaar is van onze cloud-omgeving. IT Operations zegt dat het Development is, Development zegt dat het Infrastructure is, en ondertussen heeft iedereen toegang tot de Azure Portal en maakt iedereen resources aan wanneer ze dat nodig achten. Het is de Wild West."

In een heel ander deel van het hoofdkantoor zitten de ontwikkelaars gefrustreerd naar hun schermen te staren. Huub Amster, een senior developer met tien jaar ervaring bij Ahumbo, heeft net drie dagen aan code-aanpassingen verloren omdat een collega zonder overleg de VM-configuratie heeft aangepast. Zijn smartphone vibreert constant met alerts van de productieomgeving die weer onder druk staat omdat het weekend nadert - de traditionele piek in online bestellingen.

## Project 1: Op Zoek naar Automatisering - De Ontdekking van Containers

De frustratie onder het ontwikkelteam bereikt een hoogtepunt wanneer voor de derde keer die week één van de Azure VM's overbelast raakt tijdens een deployment. Huub Amster besluit dat er een fundamentele verandering nodig is.

"Zo kunnen we niet doorgaan," zegt hij tijdens een impromptu team-vergadering. "Elke deployment is een avontuur, en niet in de goede zin van het woord. We moeten een manier vinden om het proces te automatiseren en consistenter te maken."

Het team brainstormt over mogelijke oplossingen:

"We zouden Ansible scripts kunnen schrijven om deployments te automatiseren," oppert Sarah van Dam, een backend developer.

"Of wat dacht je van Puppet of Chef voor configuratiebeheer?" voegt Jaap Klaassen, een frontend developer, toe.

Huub knikt, maar lijkt niet helemaal overtuigd. "Die tools kunnen helpen, maar ze lossen niet het fundamentele probleem op dat onze ontwikkelomgeving verschilt van de testomgeving, die weer verschilt van productie. We hebben steeds het 'het werkt op mijn machine' probleem."

Die avond doet Huub onderzoek naar moderne automatiseringsoplossingen en stuit op een blog over containerisatie en Kubernetes. Hij is meteen gefascineerd. "Dit is het," mompelt hij terwijl hij dieper duikt in de concepten. "Containers lossen het 'het werkt op mijn machine' probleem op. En Kubernetes zou onze scaling issues kunnen verhelpen."

### Het K3S Experiment

De volgende dag presenteert Huub zijn ideeën aan het team.

"Ik stel voor dat we experimenteren met containers," zegt hij enthousiast. "Maar in plaats van meteen naar Azure te gaan, laten we eerst lokaal testen met K3s, een lichtgewicht Kubernetes distributie. We kunnen een oude server uit de afgeschreven hardware stack gebruiken."

Erik Noorhuis, de teamleider, kijkt sceptisch. "Is dit niet gewoon een nieuwe technische speeltje?"

"Nee," antwoordt Huub vastberaden. "Dit gaat over fundamenteel veranderen hoe we werken. Containers kunnen ons helpen om consistentie te creëren tussen ontwikkeling, test en productie. En K3s geeft ons de mogelijkheid om dit lokaal te testen zonder grote investeringen."

Het team besluit een experiment te starten. Ze vragen een oude server uit de afgeschreven hardware stack en installeren K3s. Na enkele dagen van trial-and-error krijgen ze een klein deel van de orderverwerking werkend in containers.

De resultaten zijn opmerkelijk: de applicatie start in seconden op, gebruikt een fractie van de resources, en het beste van alles - het gedraagt zich exact hetzelfde, ongeacht waar het draait.

"Dit is precies wat we nodig hebben," zegt Sarah enthousiast. "Geen meer 'het werkt op mijn machine' excuses. De container bevat alles wat de applicatie nodig heeft."

Erik, aanvankelijk sceptisch, is onder de indruk. "En jullie zeggen dat we dit kunnen gebruiken om ook onze deployments te automatiseren?"

"Absoluut," knikt Huub. "We kunnen een CI/CD pipeline opzetten die automatisch een container bouwt, test, en deployt wanneer we code pushen. Geen handmatige stappen meer, geen inconsistenties tussen omgevingen."

### Verbeterde Flow door Containerisatie

Geïnspireerd door het succes van hun experiment, besluit het team hun aanpak uit te breiden. Ze kiezen een niet-kritieke maar belangrijke microservice uit als volgende kandidaat voor containerisatie.

Het team brengt hun huidige proces in kaart en ontdekt talloze vertragingen, handovers en inconsistenties. Ze ontwikkelen een nieuwe workflow:

1. Ontwikkelaars schrijven code in hun lokale omgeving, met containers die identiek zijn aan productie
2. Bij elke commit wordt automatisch een nieuwe container gebouwd
3. Geautomatiseerde tests worden uitgevoerd in de container
4. Bij succes wordt de container gedeployed naar de K3s testomgeving
5. Na goedkeuring kan dezelfde container met één klik naar productie

Na enkele weken van implementatie beginnen de voordelen zichtbaar te worden. Deployments die voorheen uren duurden, gebeuren nu in minuten. "Works on my machine" problemen zijn drastisch verminderd, en het team kan veel sneller reageren op klantfeedback.

"Het is verbazingwekkend hoe veel soepeler ons proces nu verloopt," merkt Lisa Wong, de QA engineer, op tijdens een retrospectieve. "De flow van code naar productie is nog nooit zo soepel geweest."

Huub knikt instemmend. "Dat is precies waar ik op hoopte. We hebben de doorstroming van werk aanzienlijk verbeterd, en dat was ons belangrijkste knelpunt."

Het succes van hun container-experiment en de verbeterde flow trekken de aandacht van andere teams binnen Ahumbo, inclusief Operations en Security.

## Project 2: De Ontdekking van De Drie Wegen en Versterken van Feedback Loops

Het succes van de K3s-implementatie heeft interesse gewekt bij andere teams binnen Ahumbo. Bram Visser, de Operations Manager, benadert Huub met een vraag.

"Jullie hebben de flow van ontwikkeling naar productie verbeterd," zegt hij, "maar we hebben nog steeds beperkt zicht op wat er in productie gebeurt. Als er problemen zijn, horen we het vaak eerst van klanten."

Huub knikt begrijpend. "Dat is inderdaad onze volgende uitdaging. We hebben de doorstroming verbeterd, maar we moeten ook beter worden in het detecteren en oplossen van problemen voordat ze klanten bereiken."

Tijdens een conferentie over DevOps hoort Huub over "De Drie Wegen van DevOps" - een raamwerk voor het denken over DevOps-transformatie. Hij deelt zijn inzichten met het uitgebreide team, nu inclusief vertegenwoordigers van Operations en Security.

"Wat we hebben gedaan in ons eerste project," legt Huub uit, "was in feite het toepassen van de Eerste Weg van DevOps - het optimaliseren van flow. We hebben knelpunten weggenomen en de doorstroming van werk van links naar rechts verbeterd, van idee naar waarde voor de klant."

"En nu ligt onze uitdaging bij wat zij de Tweede Weg noemen - het versterken van feedback loops. We hebben de stroom van links naar rechts verbeterd, maar we moeten ook de stroom van informatie van rechts naar links versterken."

Het team is geïntrigeerd door dit raamwerk.

"Er is ook een Derde Weg," vervolgt Huub. "Die gaat over een cultuur van experimenteren en continu leren. Maar laten we ons eerst richten op de Tweede Weg, aangezien dat onze meest urgente uitdaging is."

Een uitgebreid team komt samen om een volledig Kubernetes-platform te ontwikkelen met een sterke focus op observeerbaarheid en feedback, geïnspireerd door de principes van de Tweede Weg.

"De Tweede Weg draait om het versnellen van leren," legt Huub uit aan de grotere groep. "We moeten systemen bouwen die ons constant feedback geven, zodat we problemen kunnen detecteren voordat ze impact hebben op klanten."

Het team kiest voor een volwaardige Kubernetes-implementatie met uitgebreide monitoring en observability-tooling:

1. **Uitgebreide Telemetrie**: Implementatie van de LGTM-stack (Loki voor logs, Grafana voor dashboards, Tempo voor traces, en Mimir voor metrics)
2. **Real-time Alerting**: Proactieve waarschuwingen bij afwijkingen in prestaties of gedrag
3. **Automatische Scaling**: Feedback-gestuurde aanpassing van resources op basis van actuele belasting
4. **Canary Deployments**: Geleidelijke uitrol van nieuwe versies met automatische rollback bij problemen
5. **Security Scanning**: Continue vulnerability assessments van containerimages

Miranda Jansen, de Security Officer, is bijzonder enthousiast over de security-aspecten. "Door security-telemetrie direct te integreren in onze observability-tools, wordt security een integraal onderdeel van onze feedback loops, niet een afterthought."

Het team organiseert een "Feedback Day" om de nieuwe mogelijkheden te demonstreren. Ze simuleren verschillende scenario's, van performance-problemen tot security-vulnerabilities, en laten zien hoe het nieuwe platform deze detecteert en erop reageert, vaak automatisch en voordat gebruikers impact ervaren.

"Dit is de kracht van de Tweede Weg," legt Huub uit tijdens de demonstratie. "We creëren korte, constante feedback loops die ons in staat stellen om continu te leren en te verbeteren."

Aan het einde van Project 2 heeft Ahumbo niet alleen een schaalbaar Kubernetes-platform, maar ook een rijk ecosysteem van geautomatiseerde feedback dat het mogelijk maakt om snel problemen te identificeren en op te lossen, vaak voordat ze klanten bereiken.

## Project 3: Een Cultuur van Experimenteren en Leren via de Derde Weg

Een jaar na de start van hun containerisatie-reis wordt Ahumbo geconfronteerd met nieuwe uitdagingen. Geopolitieke spanningen en strengere Europese regelgeving voor dataopslag roepen vragen op over hun afhankelijkheid van Azure als Amerikaanse cloud-provider.

In een spoedvergadering van het directieteam uit Jan-Willem de Groot, de CIO, zijn zorgen: "Een Nederlandse concurrent heeft tijdelijk geen toegang meer gehad tot hun cloud-infrastructuur vanwege een conflict over naleving van Amerikaanse exportrestricties. Zijn wij wel voldoende voorbereid op een dergelijk scenario?"

Het DevSecOps-team wordt gevraagd om de mogelijkheden te onderzoeken voor een hybride of multi-cloud strategie. Bij de eerste bespreking hierover heerst onzekerheid over hoe deze uitdaging aan te pakken.

"Dit is een compleet nieuwe dimensie," zegt Bram Visser. "Tot nu toe hebben we ons gericht op flow en feedback binnen onze bestaande omgeving. Nu moeten we nadenken over portabiliteit tussen verschillende clouds."

Huub ziet hierin een kans om de Derde Weg van DevOps toe te passen. "Dit is precies waar de Derde Weg over gaat - een cultuur van experimenteren en leren. In plaats van te wachten tot er een probleem is, kunnen we proactief experimenten opzetten."

Hij legt uit hoe de Derde Weg een cultuur van nieuwsgierigheid en continue verbetering bevordert, waarbij fouten worden gezien als leermomenten in plaats van redenen voor schuld.

Het team ontwikkelt een plan voor systematisch experimenteren met multi-cloud strategieën:

1. **Soevereiniteitsanalyse**: In kaart brengen waar data momenteel wordt opgeslagen en verwerkt
2. **Exit-scenario's simuleren**: Oefeningen waarin toegang tot Azure plotseling wordt beperkt
3. **Workload-portabiliteitsexperimenten**: Testen hoe gemakkelijk applicaties kunnen worden verplaatst tussen clouds
4. **Cloud-agnostische platformontwerp**: Herontwerpen van hun Kubernetes platform om zo weinig mogelijk afhankelijk te zijn van Azure-specifieke diensten

Thomas Bauwens, een specialist in open source cloud-technologieën, wordt ingehuurd om het team te adviseren. "Jullie basis met Kubernetes is solide, maar we moeten ervoor zorgen dat jullie configuratie, monitoring, en CI/CD pipelines ook cloud-agnostisch worden."

Het project leidt niet alleen tot technische verbeteringen in hun multi-cloud capaciteiten, maar ook tot een fundamentele cultuurverandering in hoe het bedrijf met uitdagingen omgaat. Teams organiseren regelmatig "game days" waarin ze verschillende scenario's simuleren, van technische storingen tot geopolitieke uitdagingen, om hun reactievermogen te testen en te verbeteren.

"De Derde Weg gaat over meer dan alleen techniek," legt Huub uit tijdens een presentatie aan het management. "Het gaat over een organisatie die continu experimenteert, leert, en verbetert."

Hoewel de Derde Weg belangrijk is voor dit project, ligt de nadruk nog steeds op het verder verbeteren van de flow (Eerste Weg) en het versterken van feedback loops (Tweede Weg) in een multi-cloud context. Het team breidt hun CI/CD pipelines uit om deployment naar verschillende clouds te ondersteunen en implementeert cross-cloud monitoring om een consistent beeld te krijgen van hun applicaties, ongeacht waar ze draaien.

## Conclusie

De reis van Ahumbo van een traditionele "lift and shift" cloud-migratie naar een volwassen DevSecOps-organisatie begon met een eenvoudig experiment met K3s en containers om de flow van werk te verbeteren. Pas later, door de ontdekking en toepassing van De Drie Wegen van DevOps, heeft het bedrijf zijn transformatie compleet gemaakt.

De eerste twee wegen, met hun focus op het verbeteren van flow en het versterken van feedback loops, vormden de basis voor deze transformatie. Ze stelden Ahumbo in staat om sneller en betrouwbaarder waarde te leveren aan klanten, problemen vroegtijdig te detecteren en op te lossen, en uiteindelijk flexibeler te reageren op veranderende omstandigheden.

Wat begon als een zoektocht naar automatisering door een gefrustreerd ontwikkelteam, leidde uiteindelijk tot een fundamentele herziening van hoe Ahumbo software bouwt, deployt en beheert - een reis van DevOps-transformatie via de geleidelijke ontdekking en toepassing van de Drie Wegen.

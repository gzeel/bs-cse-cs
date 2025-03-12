# Les 3 - Hello, Ansible (1)!

Leerdoelen:

1. Aan het einde van deze les weet je wat Ansible is en welke relatie het heeft met de theorie van Infrastructure as Code.
2. Aan het einde van deze les kun je een aantal ad-hoc commando's op een host uitvoeren
3. Aan het einde van deze les kun je een simpel playbook schrijven en dit uitvoeren op een groep van hosts dmv een inventory.

Inhoud:

- Introductie Ansible
- Inventory
- Adhoc commando's
- Playbooks
- My first playbook
- Opdracht
- Waar hulp te krijgen?

## Introductie Ansible

Denk eens terug aan een eerder semester waarin je in een opdracht of project een server moest instellen. Waarschijnlijk voerde je toen veel commando’s handmatig uit, en had elke machine een unieke configuratie. Het was vast lastig om dit precies opnieuw te doen, zeker als je niet alles goed had gedocumenteerd, zoals welke commando’s of scripts je hebt gebruikt.

Hoe fijn zou het zijn als je met een handige tool of programmeertaal precies kunt vastleggen hoe een server ingericht moet worden? Denk aan welke applicaties geïnstalleerd moeten worden of hoe de instellingen eruit moeten zien.

Hier komt Ansible van pas. Ansible is een gratis tool waarmee je IT-taken kunt automatiseren, zoals het installeren van software, beheren van configuraties en regelen van infrastructuur. Het gebruikt een simpele taal genaamd YAML, die zowel door mensen als machines makkelijk te begrijpen is. Een groot voordeel van Ansible is dat het geen extra software (agents) nodig heeft op de servers die je beheert. Het gebruikt gewoon SSH om met die servers te communiceren, wat het eenvoudiger maakt dan andere tools zoals Puppet of Chef. Bovendien zorgt Ansible voor idempotentie. Dit betekent dat je dezelfde taak meerdere keren kunt uitvoeren zonder dat het iets kapot maakt of verandert als het al goed staat.

Omdat Ansible via SSH werkt, kun je gebruikmaken van private/public key-authenticatie. Dit heeft veel voordelen, vooral op het gebied van beveiliging en gemak:

Veiliger dan wachtwoorden: De privésleutel blijft altijd veilig bij jou, en alleen de publieke sleutel wordt op de server geplaatst. Zo kunnen wachtwoorden niet worden onderschept of gestolen.
Geen gedoe met wachtwoorden: Je hoeft niet steeds een wachtwoord in te typen, wat het werken sneller en makkelijker maakt.
Schaalbaar en flexibel: Het is eenvoudig om publieke sleutels naar nieuwe servers te sturen of oude sleutels te verwijderen. Dit is handig als bijvoorbeeld iemand het team verlaat, zonder dat je overal wachtwoorden hoeft aan te passen.

## Inventory

Ansible gebruikt een inventorybestand wat een beetje lijkt op het /etc/hosts bestand, waarin je ip adressen en namen van servers opneemt. Waar je in /etc/hosts IP-adressen koppelt aan servernamen of een fqdn, koppelt een Ansible-inventorybestand servers (IP-adressen of FQDN's) aan groepen. Namen van inventorybestanden hoeven geen bepaalde naamgevingsconventie te volgen. Je mag het inventory bestand elke willekeurige naam geven.

Voorbeeld van een stukje uit een inventory:

```ini
[voorbeeldgroep]
webserver1.voorbeeld.nl
```

waarbij voorbeeldgroep de groep servers is die je beheert en webserver1.voorbeeld.nl de FQDN (of het IP-adres) is van een server in die groep. Als je poort 22 niet gebruikt voor SSH op deze server, moet je dit toevoegen aan het adres, zoals webserver1.voorbeeldgroep.nl:2222, aangezien Ansible standaard poort 22 gebruikt en deze waarde niet krijgt van je ssh-configuratie bestand.

Je kunt je inventory ook in het standaard inventorybestand van Ansible plaatsen, /etc/ansible/hosts. Maar dat bestand vereist sudo-rechten en het is meestal beter om een losse inventory bij te houden in je Ansible-projecten.

## Modules

Ansible werkt met `modules`. Deze modules zijn vaak Python scripts (kan ook een andere taal zijn) die iets specifieks kunnen. Denk bijvoorbeeld aan het installeren van software, het starten of stoppen van een service, het aanpassen van een bestand, of het aanmaken van een gebruiker.

Ansible heeft standaard een grote verzameling ingebouwde modules (kun je later herkennen aan ansible.builtin) maar daarnaast zijn er ook veel communitymodules beschikbaar die je kunt gebruiken. Een compleet overzicht van alle beschikbare modules is [hier](https://docs.ansible.com/ansible/2.8/modules/list_of_all_modules.html) te vinden.

Zorg dat je in je commando's en playbooks altijd duidelijk aangeeft of het een ansible.builtin, community of andere soort module is. Dit noem je de FQMN (Fully Qualified Module Name).

## Adhoc commando's

Ansible gebruik je meestal met een `playbook` of een `ad-hoc` commando. Ad-hoc commando's zijn erg handig voor taken die je niet heel vaak gebruikt. Je wil bijvoorbeeld een groep machines rebooten of weten of een machine of een groep van machines benaderbaar zijn. Als je meerdere taken achter elkaar wil uitvoeren gebruik je een playbook.

De standaard module die Ansible gebruikt bij ad-hoc commando's is de module `command`. Met deze module kun je standaard Unix/Linux commando's uitvoeren maar geen geavanceerde shell dingen doen zoals pipe en redirect. Daar is de module `shell` beter in.

Maar stel je wil een reboot uitvoeren van een groep machines:

```bash
ansible -i inventory.ini voorbeeldgroep -a "/sbin/reboot" -u [username] --become -K
```

Je ziet hier de opties `--become` en `-K` omdat je waarschijnlijk root rechten nodig hebt voor het rebooten. Met `--become` geef je aan dat je root wil worden en met `-K` dat je je sudo wachtwoord op wil geven.

Pingen werkt net zoals je waarschijnlijk al wel eens gedaan hebt. Dat kun je met het ping commando doen zoals je waarschijnlijk wel eens gedaan hebt. Als je dat met ansible zou willen doen kan je commando er ongeveer zo uit zien:
Ping:

```bash
ansible -i inventory.ini voorbeeldgroep -a "ping -c 4 {{ inventory_hostname }}" -u [username]
```

Met dit commando zal Ansible naar elke host in de groep 'voorbeeldgroep' 4 pings sturen. Nadeel hiervan is dat je bij elke host op 4 pings moet wachten en je eigenlijk alleen weet dat de host up is.

Maar de command module is niet echt `idempotent`, waar we het in les-01 over gehad hebben. Door een shell commando te gebruiken hebben we geen foutafhandeling, krijgen we geen respons terug etc. Daarom is het handig om de standaard modules van Ansible te gebruiken voor dit soort taken.
Bijvoorbeeld de `ping` module. Voordeel van het gebruik van deze module is ook dat je gelijk weet of de host op ssh benaderbaar is en het wachtwoord of het ssh-keypair klopt.

```bash
ansible -i inventory.ini voorbeeldgroep -m ansible.builtin.ping -u [username]
```

Je ziet dat het commando een stuk korter is geworden.
Als alles werkt, zal je een bericht zien als `webserver1.voorbeeld.nl | SUCCES >>`, en dan het resultaat van je ping. Als het niet werkt, voer je de opdracht opnieuw uit met -vvvv aan het einde om uitgebreide uitvoer te zien. De kans is groot dat je SSH-sleutels niet correct hebt geconfigureerd.

Een ander voorbeeld is de copy module

```bash
ansible -i inventory.ini voorbeeldgroep -m ansible.builtin.file -a "dest=/tmp/test/a.txt mode=600 owner=gebruiker group=gebruikers"
```

Je ziet dat de code declative is geworden, je geeft alleen maar aan welke file het moet zijn, welke rechten en wie de eigenaar is. Hoe het gedaan moet worden mag de Ansible module uitzoeken.

Ansible-modules zijn handiger in gebruik dan bash-commando's via het `-a` argument omdat ze speciaal ontworpen zijn om veelvoorkomende taken simpel en efficiënt uit te voeren. Met een module geef je alleen aan wat je wilt bereiken, zoals een pakket installeren of een bestand aanpassen, en Ansible regelt de rest. Dit scheelt je het schrijven van exacte commando's.

Daarnaast zijn modules slim genoeg om te controleren of iets al goed staat voordat ze actie ondernemen, wat voorkomt dat taken onnodig opnieuw worden uitgevoerd. Dit maakt je automatisering niet alleen overzichtelijker en betrouwbaarder, maar ook beter schaalbaar en makkelijker te begrijpen voor anderen.

## Playbooks

Het is natuurlijk niet handig als je een aantal van dit commando's achter elkaar uit moet voeren. Zeker niet als het handmatig moet. Ansible heeft hier als oplossing playbooks voor. De vertaling draaiboek pas er heel goed bij. In het draaiboek staan de taken beschreven die Ansible (achter elkaar) uit moet voeren.

Een Ansible Playbook is geschreven in YAML-formaat, wat een menselijk leesbare en machine-verwerkbare taal is. Het Playbook bestaat uit een reeks van 'plays', die elk bestaan uit een of meer 'tasks'. Elke taak beschrijft een specifieke actie die moet worden uitgevoerd, zoals het installeren van software, het aanpassen van configuratiebestanden, het controleren van de status van een dienst, en meer. Deze taken kunnen ook variabelen, voorwaardelijke verklaringen (conditions) en lussen (loops) bevatten om de automatisering flexibel en aanpasbaar te maken voor verschillende scenario's.

Een voorbeeld playbook:

```yaml
 1 ---
 2 - hosts: all
 3   become: yes
 4
 5   tasks:
 6   - name: Ensure chrony (for time synchronization) is installed.
 7     ansible.builtin.apt:
 8       name: chrony
 9       state: present
10
11   - name: Ensure chrony is running.
12     ansible.builtin.service:
13       name: chronyd
14       state: started”
```

Wat zou dit playbook doen?
Laten we er stap voor stap door heen gaan:

```yaml
1 ---
```

Deze eerste regel is een markering die aangeeft dat de rest van het document zal worden opgemaakt in YAML.

```yaml
2 - hosts: all
```

Deze regel vertelt Ansible op welke hosts dit draaiboek van toepassing is. Hier wordt aangegeven dat het op alle hosts uit de opgegeven inventory uitgevoerd moet worden.

```yaml
3 - become: yes
```

Omdat we root toegang nodig hebben om chrony te installeren en de systeemconfiguratie te wijzigen, vertelt deze regel Ansible om sudo te gebruiken voor alle taken in het draaiboek (je vertelt Ansible om de rootgebruiker te 'worden' met sudo, of een equivalent).

```yaml
5 tasks:
```

Nu volgt de opsomming van taken die uitgevoerd moeten worden. Alle taken na deze regel worden uitgevoerd op alle hosts (want hosts was all)

```yaml
6   - name: Ensure chrony (for time synchronization) is installed.
7     ansible.builtin.apt:
8       name: chrony
9       state: present”
```

Deze opdracht is hetzelfde als het uitvoeren van yum install chrony, maar het is veel intelligenter; het zal controleren of chrony is geïnstalleerd, en zo niet, installeer het dan. Je zou dit ook kunnen doen met het volgende shellscript:

```bash
if ! rpm -qa | grep -qw chrony; then
    apt install -y chrony
fi
```

Het bovenstaande script is echter nog steeds niet zo robuust als het yum-commando van Ansible. Wat als een ander pakket met chrony in zijn naam is geïnstalleerd, maar niet chrony? Dit script zou extra aanpassingen en complexiteit vereisen om overeen te komen met het eenvoudige Ansible yum-commando.

```yaml
11   - name: Ensure chrony is running.
12     ansible.builtin.service:
13       name: chronyd
14       state: started
15       enabled: yes
```

Deze laatste taak controleert en zorgt ervoor dat de chronyd-service wordt gestart en uitgevoerd, en stelt deze in om te starten bij het opstarten van het systeem. Een shellscript met hetzelfde effect zou zijn:

```bash
# Start chronyd if it's not already running.
if ps aux | grep -q "[c]hronyd"
then
    echo "chronyd is running." > /dev/null
else
    systemctl start chronyd.service > /dev/null
    echo "Started chronyd."
fi
# Make sure chronyd is enabled on system startup.
systemctl enable chronyd.service
```

Hier zie je hoe de dingen ingewikkeld worden in het land van shell-scripts! En dit shellscript is nog steeds niet zo robuust als wat je krijgt met Ansible. Om idempotentie te behouden en foutcondities af te handelen, moet je nog meer werk doen met eenvoudige shellscripts dan met Ansible.

Net als bij code- en configuratiebestanden is documentatie in Ansible (bijvoorbeeld het gebruik van de name-parameter en/of het toevoegen van opmerkingen aan de YAML voor gecompliceerde taken) niet absoluut noodzakelijk. Maar zorg ervoor dat je taken een logische naam hebben met wat ze doen (dit is ook verplicht voor de opdrachten). Dit helpt ook wanneer je de playbooks moet overdragen, zodat je kunt laten zien wat er gebeurt in een voor mensen leesbaar formaat.

## Meerdere machines combineren

Hieronder nog een wat realistischer en complexer voorbeeld met 2 applicatie of webservers en een database server.

Er zijn veel manieren waarop je aan Ansible duidelijk kunt maken welke servers je beheert, maar de meest standaard en eenvoudigste is om ze toe te voegen aan een inventorybestand dat je opslaat in de directory van je Ansible-project.

In de eerdere voorbeelden specificeerden we het pad naar het inventarisbestand op de opdrachtregel met behulp van -i inventory. Je kunt ook in `/etc/ansible/ansible.cfg` of in de map waarin je werkt in `ansible.cfg` het volgende configureren:

```ini
1 [defaults]
2 inventory = inventory.ini
```

Het verschil in applicatie/webservers en de database server kun je als volgt in een inventory opnemen

```ini
 1 [all]
 2 app-server1 ansible_host=192.168.60.4
 3 app-server2 ansible_host=192.168.60.5
 4 database-server1 ansible_host=192.168.60.6
 5
 6 [app]
 7 app-server1 ansible_host=192.168.60.4
 8 app-server2 ansible_host=192.168.60.5
 9
10 [db]
11 database-server1 ansible_host=192.168.60.6
12
13
14 [all:vars]
15 ansible_user=ansible
16 ansible_ssh_private_key_file=~/.ssh/key
```

1. Het eerste blok plaatst alle drie de machines in de groep [all].
1. Het tweede blok plaatst beide applicatieservers in het [app] blok.
1. Het derde blok plaats de database server in het [db] blok.
1. Het vierde blok geeft een aantal variabelen aan alle servers in de groep 'all'.

Met deze inventory hebben kun je ook playbooks uitvoeren op de verschillende hosts.
Stel, we willen op de web/app servers een bepaald pakket (chrony) geinstalleerd hebben en op de database servers wat anders (curl). Dan kun je met hosts aangeven op welke groep servers je de taken uitgevoerd wil hebben:
Als je dit in 1 playbook zou willen uitvoeren ziet het playbook het er als volgt uit:

```yaml
---
- hosts: app
  become: true

  tasks:
    - name: Ensure chrony is installed
      ansible.builtin.apt:
        name: chrony
        state: present

    - name: Ensure chrony is started
      ansible.builtin.service:
        name: chronyd
        state: started
        enabled: true

- hosts: db
  become: true

  tasks:
    - name: Ensure curl is installed
      ansible.builtin.apt:
        name: curl
        state: present
```

Het playbook kun je uitvoeren met het volgende commando:

```bash
ansible-playbook playbook.yml
```

> Opdracht 1
>
> - Maak een nieuwe repository les-03 aan.
> - Maak een nieuwe git branch `test` aan en werk voor opdracht 1 en 2 in deze branch.
> - Deploy met Terraform een VM en zorg dat je in kunt loggen op deze vm dmv een ssh-key. Zorg dat er bij het deployen van deze VM automatisch een inventory wordt aangemaakt.

> Opracht 2
>
> - In de `test` branch:
> - Maak playbooks voor de volgende taken:
> - Alle packages op een Ubuntu VM moeten geupdate worden.
> - Het bestand /etc/hosts op de VM moet aangepast worden, er moet een regel toegevoegd worden in /etc/hosts toe die naar je esxi server wijst. Noem de host esxi.
> - Een user `test` toevoegen op de VM
> - Een lokaal bestand wordt gekopieerd naar de VM
> - Maak een playbook dat /etc/ en /var/www/ back-upt, voeg een cronjob toe die dagelijks een back-up maakt en kopieer dit naar /tmp
> - Voer de code uit op de VM van opdracht 1

> Opdracht 3
>
> - Gebruik de repository van opdracht 1, maak een nieuwe branch `productie` aan
> - Deploy met Terraform drie VMs (vanuit 1 manifest) en zorg dat je in kunt loggen op deze vm's dmv een ssh-key. Zorg dat er bij het deployen van deze vm's automatisch een inventory wordt aangemaakt. Er zijn 2 webservers en 1 database server.

> Opdracht 4
>
> - In de `productie` branch:
> - Schrijf een playbook wat op twee webservers nginx installeert en op de database server mariadb. Het playbook moet gebruik maken van de groepen uit de inventory van Opdracht 3.

> Opdracht 5
>
> - In een branch `proxmox`
> - Schrijf een playbook dat van een Proxmox Hypervisor alle VM's backupped. Gebruik de volgende waardes: api gebruiker en wachtwoord is `test`, de api host is node1, en de storage waarop de backups opgeslagen moeten worden heet `backup_vm`. Voor deze opdracht moet de juiste proxmox community module gebruikt worden.
> - Je kunt dit playbook uiteraard niet testen.

Lever de code van opdracht 4 deze week in op Brightspace.

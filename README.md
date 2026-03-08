# Mantova Ambiente per Home Assistant

Integrazione custom per Home Assistant che espone il calendario di raccolta rifiuti di Mantova Ambiente.

Funzioni principali:

- configurazione da interfaccia con scelta zona
- supporto a più istanze, anche sulla stessa zona
- sensori per prossima raccolta, raccolte di oggi e domani e prossima data per ogni frazione
- binary sensor per sapere se una frazione viene raccolta oggi o domani

Installazione con HACS:

1. Aggiungi questo repository come custom repository di tipo `Integration`
2. Installa `Mantova Ambiente`
3. Riavvia Home Assistant
4. Aggiungi l'integrazione dalla UI

Note:

- Questo progetto è non ufficiale e non è affiliato, approvato o mantenuto da TEA S.p.A., Mantova Ambiente o società collegate.
- I calendari di raccolta possono cambiare. Verifica sempre le informazioni importanti tramite i canali ufficiali di Mantova Ambiente.
- Il software è fornito così com'è, senza garanzie. L'utente è responsabile di notifiche, automazioni e conseguenze derivanti dall'uso dell'integrazione.

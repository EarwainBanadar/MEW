# KONTEXTBLOCK – AP9.3.5.2 Release Builder

1. Jedes Release besitzt eine eindeutige Release-ID und Version.
2. Jedes Artefakt wird durch SHA-256 und Dateigröße abgesichert.
3. Pflichtartefakte blockieren den Build, wenn sie fehlen.
4. Artefakte außerhalb des Source Root werden zurückgewiesen.
5. Das Manifest wird deterministisch sortiert.
6. Das Release-Archiv verwendet normierte ZIP-Zeitstempel.
7. Änderungen nach der Inventarisierung blockieren den Build.
8. Die Release-Verifikation prüft Existenz, Größe und SHA-256.
9. Ein leeres Release ist unzulässig.
10. Release-Metadaten und Artefaktinventar bleiben getrennt.

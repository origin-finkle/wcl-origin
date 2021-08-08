---{{ $logs := index (index $.Site.Data.raids .Name) "logs" }}
title: "{{ $logs.title }} - {{ .Name }}"
reportCode: "{{ .Name }}"
date: {{ dateFormat "2006-01-02" (time (int (div $logs.startTime 1000))) }}
---
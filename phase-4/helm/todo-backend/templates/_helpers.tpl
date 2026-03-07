{{/*
Expand the name of the chart.
*/}}
{{- define "todo-backend.name" -}}
{{- .Chart.Name }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todo-backend.fullname" -}}
{{- .Release.Name }}-{{ .Chart.Name }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-backend.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{ include "todo-backend.selectorLabels" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo-backend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-backend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

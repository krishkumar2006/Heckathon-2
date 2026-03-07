{{/*
Expand the name of the chart.
*/}}
{{- define "todo-frontend.name" -}}
{{- .Chart.Name }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todo-frontend.fullname" -}}
{{- .Release.Name }}-{{ .Chart.Name }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-frontend.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{ include "todo-frontend.selectorLabels" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo-frontend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-frontend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

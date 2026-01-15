{{/*
Expand the name of the chart.
*/}}
{{- define "service.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "service.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "service.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Name of the ServiceComponent api.
*/}}
{{- define "api.name" -}}
{{ include "service.name" . }}-api
{{- end }}

{{/*
ServiceComponent api labels
*/}}
{{- define "api.labels" -}}
helm.sh/chart: {{ include "service.chart" . }}
{{ include "api.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.ServiceComponent }}
{{- end }}

{{/*
ServiceComponent api selector labels
*/}}
{{- define "api.selectorLabels" -}}
app.kubernetes.io/service: {{ include "service.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
service: {{ .Chart.Name }}
app.kubernetes.io/servicecomponent: {{ .Values.api.name }}
isMainInterface: "yes"
tier: {{ .Values.api.tier}}
{{- end }}

{{/*
Name of the ServiceComponent db.
*/}}
{{- define "db.name" -}}
{{ include "service.name" . }}-db
{{- end }}

{{/*
ServiceComponent db labels
*/}}
{{- define "db.labels" -}}
helm.sh/chart: {{ include "service.chart" . }}
{{ include "db.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.ServiceComponent }}
{{- end }}

{{/*
ServiceComponent db selector labels
*/}}
{{- define "db.selectorLabels" -}}
app.kubernetes.io/service: {{ include "service.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
service: {{ .Chart.Name }}
app.kubernetes.io/servicecomponent: {{ .Values.db.name }}
isMainInterface: "no"
tier: {{ .Values.db.tier}}
{{- end }}

{{/*
Name of the ServiceComponent prc.
*/}}
{{- define "prc.name" -}}
{{ include "service.name" . }}-prc
{{- end }}

{{/*
ServiceComponent prc labels
*/}}
{{- define "prc.labels" -}}
helm.sh/chart: {{ include "service.chart" . }}
{{ include "prc.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.ServiceComponent }}
{{- end }}

{{/*
ServiceComponent prc selector labels
*/}}
{{- define "prc.selectorLabels" -}}
app.kubernetes.io/service: {{ include "service.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
service: {{ .Chart.Name }}
app.kubernetes.io/servicecomponent: {{ .Values.prc.name }}
isMainInterface: "no"
tier: {{ .Values.prc.tier}}
{{- end }}

{{/*
Name of the ServiceComponent tm.
*/}}
{{- define "tm.name" -}}
{{ include "service.name" . }}-tm
{{- end }}

{{/*
ServiceComponent tm labels
*/}}
{{- define "tm.labels" -}}
helm.sh/chart: {{ include "service.chart" . }}
{{ include "tm.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.ServiceComponent }}
{{- end }}

{{/*
ServiceComponent tm selector labels
*/}}
{{- define "tm.selectorLabels" -}}
app.kubernetes.io/service: {{ include "service.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
service: {{ .Chart.Name }}
app.kubernetes.io/servicecomponent: {{ .Values.tm.name }}
isMainInterface: "no"
tier: {{ .Values.tm.tier}}
{{- end }}

{{/*
Name of the ServiceComponent im.
*/}}
{{- define "im.name" -}}
{{ include "service.name" . }}-im
{{- end }}

{{/*
ServiceComponent im labels
*/}}
{{- define "im.labels" -}}
helm.sh/chart: {{ include "service.chart" . }}
{{ include "im.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.ServiceComponent }}
{{- end }}

{{/*
ServiceComponent im selector labels
*/}}
{{- define "im.selectorLabels" -}}
app.kubernetes.io/service: {{ include "service.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
service: {{ .Chart.Name }}
app.kubernetes.io/servicecomponent: {{ .Values.im.name }}
isMainInterface: "no"
tier: {{ .Values.im.tier}}
{{- end }}

{{/*
Name of the ServiceComponent cronjob.
*/}}
{{- define "cronjob.name" -}}
{{ include "service.name" . }}-cronjob
{{- end }}


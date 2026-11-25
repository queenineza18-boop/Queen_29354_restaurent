<#
.SYNOPSIS
  Build docs/proposal/proposal.docx from docs/proposal/proposal.md.

.DESCRIPTION
  No dependencies beyond Windows PowerShell 5.1 (.NET ZipFile): it writes the six
  OOXML parts of a .docx and packages them as a ZIP.

  Format follows the assignment: Times New Roman 12 pt body, headings 13-16 pt
  bold, line spacing 1.15, justified body text.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\make_proposal_docx.ps1
#>

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$src  = Join-Path $root "docs\proposal\proposal.md"
$out  = Join-Path $root "docs\proposal\proposal.docx"

$FONT   = "Times New Roman"
$BULLET = [string][char]0x2022

function Esc([string]$s) {
  return $s.Replace("&", "&amp;").Replace("<", "&lt;").Replace(">", "&gt;")
}

# One run; $size is in half-points.
function Run([string]$text, [bool]$bold, [int]$size) {
  $rpr = '<w:rFonts w:ascii="' + $FONT + '" w:hAnsi="' + $FONT + '" w:cs="' + $FONT + '"/>'
  if ($bold) { $rpr += '<w:b/>' }
  $rpr += '<w:sz w:val="' + $size + '"/><w:szCs w:val="' + $size + '"/>'
  return '<w:r><w:rPr>' + $rpr + '</w:rPr><w:t xml:space="preserve">' + (Esc $text) + '</w:t></w:r>'
}

# Split **bold** spans into separate runs.
function Inline([string]$text, [int]$size, [bool]$bold) {
  $parts = [regex]::Split($text, '\*\*(.+?)\*\*')
  $sb = New-Object System.Text.StringBuilder
  for ($i = 0; $i -lt $parts.Count; $i++) {
    if ([string]::IsNullOrEmpty($parts[$i])) { continue }
    $isBold = $bold -or (($i % 2) -eq 1)
    [void]$sb.Append((Run $parts[$i] $isBold $size))
  }
  return $sb.ToString()
}

function Para([string]$runs, [int]$before, [int]$after, [bool]$justify) {
  $jc = if ($justify) { "both" } else { "left" }
  return '<w:p><w:pPr><w:spacing w:before="' + $before + '" w:after="' + $after +
         '" w:line="276" w:lineRule="auto"/><w:jc w:val="' + $jc + '"/></w:pPr>' + $runs + '</w:p>'
}

function ConvertMarkdown([string]$md) {
  $sb = New-Object System.Text.StringBuilder
  foreach ($raw in ($md -split "`r?`n")) {
    $line = $raw.TrimEnd()
    if ($line.Trim().Length -eq 0) { continue }

    if ($line.StartsWith("### ")) {
      [void]$sb.Append((Para (Inline $line.Substring(4) 28 $true) 200 100 $false))
    }
    elseif ($line.StartsWith("## ")) {
      [void]$sb.Append((Para (Inline $line.Substring(3) 30 $true) 240 120 $false))
    }
    elseif ($line.StartsWith("# ")) {
      [void]$sb.Append((Para (Inline $line.Substring(2) 32 $true) 0 160 $false))
    }
    elseif ($line.StartsWith("- ")) {
      $ppr = '<w:pPr><w:spacing w:before="0" w:after="60" w:line="276" w:lineRule="auto"/>' +
             '<w:ind w:left="567" w:hanging="284"/><w:jc w:val="both"/></w:pPr>'
      [void]$sb.Append('<w:p>' + $ppr + (Run ($BULLET + " ") $false 24) +
                       (Inline $line.Substring(2) 24 $false) + '</w:p>')
    }
    else {
      [void]$sb.Append((Para (Inline $line 24 $false) 0 120 $true))
    }
  }
  return $sb.ToString()
}

$document = { param($body) @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body>$body
<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>
<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"
 w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>
</w:body></w:document>
"@ }

$styles = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:docDefaults><w:rPrDefault><w:rPr>
<w:rFonts w:ascii="$FONT" w:hAnsi="$FONT" w:cs="$FONT"/>
<w:sz w:val="24"/><w:szCs w:val="24"/><w:lang w:val="en-US"/>
</w:rPr></w:rPrDefault>
<w:pPrDefault><w:pPr>
<w:spacing w:after="120" w:line="276" w:lineRule="auto"/>
<w:jc w:val="both"/>
</w:pPr></w:pPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal">
<w:name w:val="Normal"/><w:qFormat/></w:style>
</w:styles>
"@

$contentTypes = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
</Types>
"@

$rels = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
</Relationships>
"@

$docRels = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>
"@

$core = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:title>ROSTS - Phase 0 Proposal</dc:title>
<dc:creator>Queen Ineza (29354)</dc:creator>
</cp:coreProperties>
"@

$md = Get-Content -Raw -Encoding UTF8 $src
$body = ConvertMarkdown $md

# OOXML requires forward slashes in part names, so the archive is written entry by
# entry instead of zipping a temporary folder (which would emit backslashes on Windows).
$parts = [ordered]@{
  "[Content_Types].xml"           = $contentTypes
  "_rels/.rels"                   = $rels
  "word/document.xml"             = (& $document $body)
  "word/styles.xml"               = $styles
  "word/_rels/document.xml.rels"  = $docRels
  "docProps/core.xml"             = $core
}

if (Test-Path $out) { Remove-Item $out -Force }
$utf8 = New-Object System.Text.UTF8Encoding($false)
$zip = [System.IO.Compression.ZipFile]::Open($out, [System.IO.Compression.ZipArchiveMode]::Create)
try {
  foreach ($name in $parts.Keys) {
    $entry  = $zip.CreateEntry($name, [System.IO.Compression.CompressionLevel]::Optimal)
    $stream = $entry.Open()
    $bytes  = $utf8.GetBytes($parts[$name])
    $stream.Write($bytes, 0, $bytes.Length)
    $stream.Dispose()
  }
} finally {
  $zip.Dispose()
}

$size = (Get-Item $out).Length
Write-Host "wrote $out ($size bytes)"

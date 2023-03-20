$word = new-object -ComObject word.application
$word.Visible = $false

$source_dir = 'C:/Chapter_Summarizer_GPT4/chapters_doc/'
$dest_dir = 'C:/Chapter_Summarizer_GPT4/chapters_txt/'
$saveFormat = [Enum]::Parse([Microsoft.Office.Interop.Word.WdSaveFormat], "wdFormatText");


$files = Get-ChildItem -Path $source_dir | Where-Object {$_.Name -like "*.docx"}

foreach ($file in $files)
    {
    Write-Host $file
    # accept all
    $doc = $word.Documents.Open($file.FullName)
    #$doc.Revisions.AcceptAll()
    $newname = $file.Name.Replace(".docx",".txt")
    $doc.SaveAs([ref]($dest_dir + $newname), [ref]$saveFormat)
    $doc.Close()
    # reject all
    #$doc = $word.Documents.Open($file.FullName)
    #$doc.Revisions.RejectAll()
    #$newname = $file.Name.Replace(".docx","_rejected.txt")
    #$doc.SaveAs([ref]($dest_dir + $newname), [ref]$saveFormat)
    #$doc.Close()
    }
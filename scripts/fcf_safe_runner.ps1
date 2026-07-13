[CmdletBinding()]
param(
    [Alias("SelfTest")]
    [switch]$RunSelfTest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"


function ConvertTo-FcfProcessArgument {
    [CmdletBinding()]
    param(
        [AllowEmptyString()]
        [string]$Value
    )

    if ($null -eq $Value) {
        return '""'
    }

    if (
        $Value.Length -gt 0 -and
        $Value -notmatch '[\s"]'
    ) {
        return $Value
    }

    $Builder = New-Object System.Text.StringBuilder
    [void]$Builder.Append([char]34)

    $BackslashCount = 0

    foreach ($Character in $Value.ToCharArray()) {
        if ($Character -eq [char]92) {
            $BackslashCount++
            continue
        }

        if ($Character -eq [char]34) {
            if ($BackslashCount -gt 0) {
                [void]$Builder.Append(
                    [char]92,
                    ($BackslashCount * 2) + 1
                )
            } else {
                [void]$Builder.Append([char]92)
            }

            [void]$Builder.Append([char]34)
            $BackslashCount = 0
            continue
        }

        if ($BackslashCount -gt 0) {
            [void]$Builder.Append(
                [char]92,
                $BackslashCount
            )
            $BackslashCount = 0
        }

        [void]$Builder.Append($Character)
    }

    if ($BackslashCount -gt 0) {
        [void]$Builder.Append(
            [char]92,
            $BackslashCount * 2
        )
    }

    [void]$Builder.Append([char]34)

    return $Builder.ToString()
}


function Join-FcfProcessArguments {
    [CmdletBinding()]
    param(
        [string[]]$ArgumentList = @()
    )

    $Converted = foreach ($Argument in $ArgumentList) {
        ConvertTo-FcfProcessArgument -Value $Argument
    }

    return $Converted -join " "
}


function Write-FcfLogRecord {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$LogPath,

        [Parameter(Mandatory = $true)]
        [AllowEmptyCollection()]
        [AllowEmptyString()]
        [string[]]$Lines
    )

    $Directory = Split-Path -Parent $LogPath

    if (
        $Directory -and
        -not (Test-Path $Directory)
    ) {
        New-Item `
            -ItemType Directory `
            -Path $Directory `
            -Force |
            Out-Null
    }

    $Encoding = New-Object System.Text.UTF8Encoding($false)
    $SafeLines = foreach ($Line in $Lines) {
        if ($null -eq $Line -or $Line -eq "") {
            "<EMPTY>"
        } else {
            [string]$Line
        }
    }

    $Text = ($SafeLines -join "`r`n") + "`r`n"

    [System.IO.File]::AppendAllText(
        $LogPath,
        $Text,
        $Encoding
    )
}


function Invoke-FcfProcess {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,

        [string[]]$ArgumentList = @(),

        [Parameter(Mandatory = $true)]
        [string]$WorkingDirectory,

        [Parameter(Mandatory = $true)]
        [string]$LogPath,

        [int[]]$AllowedExitCodes = @(0),

        [string]$Operation = "PROCESS"
    )

    if (-not (Test-Path $WorkingDirectory -PathType Container)) {
        throw "Working directory does not exist: $WorkingDirectory"
    }

    $StartInfo = New-Object System.Diagnostics.ProcessStartInfo
    $StartInfo.FileName = $FilePath
    $StartInfo.Arguments = Join-FcfProcessArguments `
        -ArgumentList $ArgumentList
    $StartInfo.WorkingDirectory = $WorkingDirectory
    $StartInfo.UseShellExecute = $false
    $StartInfo.RedirectStandardOutput = $true
    $StartInfo.RedirectStandardError = $true
    $StartInfo.CreateNoWindow = $true

    $Process = New-Object System.Diagnostics.Process
    $Process.StartInfo = $StartInfo

    $StartedAt = [DateTime]::UtcNow

    try {
        $Started = $Process.Start()

        if (-not $Started) {
            throw "Process did not start."
        }

        $StdOutTask = $Process.StandardOutput.ReadToEndAsync()
        $StdErrTask = $Process.StandardError.ReadToEndAsync()

        $Process.WaitForExit()

        $StdOut = $StdOutTask.Result
        $StdErr = $StdErrTask.Result
        $ExitCode = $Process.ExitCode
    } catch {
        Write-FcfLogRecord `
            -LogPath $LogPath `
            -Lines @(
                "=== FCF PROCESS START FAILURE ==="
                "operation=$Operation"
                "file=$FilePath"
                "error=$($_.Exception.Message)"
            )

        throw
    } finally {
        $Process.Dispose()
    }

    $FinishedAt = [DateTime]::UtcNow
    $DurationMs = [int](
        $FinishedAt - $StartedAt
    ).TotalMilliseconds

    $Succeeded = $AllowedExitCodes -contains $ExitCode

    Write-FcfLogRecord `
        -LogPath $LogPath `
        -Lines @(
            "=== FCF PROCESS RESULT ==="
            "operation=$Operation"
            "file=$FilePath"
            "arguments=$($StartInfo.Arguments)"
            "exit_code=$ExitCode"
            "succeeded=$Succeeded"
            "duration_ms=$DurationMs"
            "--- STDOUT BEGIN ---"
            $StdOut.TrimEnd()
            "--- STDOUT END ---"
            "--- STDERR BEGIN ---"
            $StdErr.TrimEnd()
            "--- STDERR END ---"
        )

    return [pscustomobject]@{
        Operation = $Operation
        FilePath = $FilePath
        Arguments = $StartInfo.Arguments
        ExitCode = $ExitCode
        Succeeded = $Succeeded
        StdOut = $StdOut
        StdErr = $StdErr
        DurationMs = $DurationMs
    }
}


function Invoke-FcfProcessWithRetry {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,

        [string[]]$ArgumentList = @(),

        [Parameter(Mandatory = $true)]
        [string]$WorkingDirectory,

        [Parameter(Mandatory = $true)]
        [string]$LogPath,

        [int[]]$AllowedExitCodes = @(0),

        [ValidateRange(1, 10)]
        [int]$MaxAttempts = 1,

        [ValidateRange(0, 300)]
        [int]$DelaySeconds = 0,

        [string]$Operation = "PROCESS"
    )

    $LastResult = $null

    for (
        $Attempt = 1
        $Attempt -le $MaxAttempts
        $Attempt++
    ) {
        $LastResult = Invoke-FcfProcess `
            -FilePath $FilePath `
            -ArgumentList $ArgumentList `
            -WorkingDirectory $WorkingDirectory `
            -LogPath $LogPath `
            -AllowedExitCodes $AllowedExitCodes `
            -Operation "$Operation-ATTEMPT-$Attempt"

        $LastResult |
            Add-Member `
                -MemberType NoteProperty `
                -Name AttemptCount `
                -Value $Attempt `
                -Force

        if ($LastResult.Succeeded) {
            return $LastResult
        }

        if (
            $Attempt -lt $MaxAttempts -and
            $DelaySeconds -gt 0
        ) {
            Start-Sleep -Seconds $DelaySeconds
        }
    }

    return $LastResult
}


function Get-FcfRepositoryState {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepositoryPath,

        [Parameter(Mandatory = $true)]
        [string]$LogPath
    )

    $BranchResult = Invoke-FcfProcess `
        -FilePath "git.exe" `
        -ArgumentList @(
            "branch"
            "--show-current"
        ) `
        -WorkingDirectory $RepositoryPath `
        -LogPath $LogPath `
        -Operation "GIT-BRANCH"

    $HeadResult = Invoke-FcfProcess `
        -FilePath "git.exe" `
        -ArgumentList @(
            "rev-parse"
            "HEAD"
        ) `
        -WorkingDirectory $RepositoryPath `
        -LogPath $LogPath `
        -Operation "GIT-HEAD"

    $StatusResult = Invoke-FcfProcess `
        -FilePath "git.exe" `
        -ArgumentList @(
            "status"
            "--porcelain=v1"
        ) `
        -WorkingDirectory $RepositoryPath `
        -LogPath $LogPath `
        -Operation "GIT-STATUS"

    foreach ($Result in @(
        $BranchResult
        $HeadResult
        $StatusResult
    )) {
        if (-not $Result.Succeeded) {
            throw "Repository state command failed: $($Result.Operation)"
        }
    }

    $StatusLines = @(
        $StatusResult.StdOut -split "\r?\n" |
            Where-Object { $_ }
    )

    return [pscustomobject]@{
        Branch = $BranchResult.StdOut.Trim()
        Head = $HeadResult.StdOut.Trim()
        StatusLines = $StatusLines
        IsClean = $StatusLines.Count -eq 0
    }
}


function Assert-FcfRepositoryState {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepositoryPath,

        [Parameter(Mandatory = $true)]
        [string]$LogPath,

        [Parameter(Mandatory = $true)]
        [string]$ExpectedBranch,

        [string]$ExpectedHead = "",

        [switch]$RequireClean
    )

    $State = Get-FcfRepositoryState `
        -RepositoryPath $RepositoryPath `
        -LogPath $LogPath

    if ($State.Branch -ne $ExpectedBranch) {
        throw "Unexpected branch: $($State.Branch)"
    }

    if (
        $ExpectedHead -and
        $State.Head -ne $ExpectedHead
    ) {
        throw "Unexpected HEAD: $($State.Head)"
    }

    if (
        $RequireClean -and
        -not $State.IsClean
    ) {
        throw "Repository is not clean."
    }

    return $State
}


function Assert-FcfChangedPaths {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$ActualPaths,

        [Parameter(Mandatory = $true)]
        [string[]]$ExpectedPaths
    )

    $Actual = @(
        $ActualPaths |
            Sort-Object -Unique
    )

    $Expected = @(
        $ExpectedPaths |
            Sort-Object -Unique
    )

    if (
        ($Actual -join "`n") -ne
        ($Expected -join "`n")
    ) {
        throw "Changed path set does not match expected paths."
    }

    return $true
}


function Write-FcfTextFile {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [AllowEmptyString()]
        [string]$Content,

        [ValidateSet("LF", "CRLF")]
        [string]$LineEnding = "LF"
    )

    $Normalized = $Content.Replace(
        "`r`n",
        "`n"
    ).Replace(
        "`r",
        "`n"
    ).TrimEnd("`n")

    if ($LineEnding -eq "CRLF") {
        $Normalized = $Normalized.Replace(
            "`n",
            "`r`n"
        ) + "`r`n"
    }

    if ($LineEnding -eq "LF") {
        $Normalized = $Normalized + "`n"
    }

    $Directory = Split-Path -Parent $Path

    if (
        $Directory -and
        -not (Test-Path $Directory)
    ) {
        New-Item `
            -ItemType Directory `
            -Path $Directory `
            -Force |
            Out-Null
    }

    $Encoding = New-Object System.Text.UTF8Encoding($false)

    [System.IO.File]::WriteAllText(
        $Path,
        $Normalized,
        $Encoding
    )
}


function Write-FcfCheckpoint {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [hashtable]$State
    )

    $TemporaryPath = "$Path.tmp"
    $Json = $State | ConvertTo-Json -Depth 10

    Write-FcfTextFile `
        -Path $TemporaryPath `
        -Content $Json `
        -LineEnding "LF"

    Move-Item `
        -Path $TemporaryPath `
        -Destination $Path `
        -Force
}


function Read-FcfCheckpoint {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path $Path -PathType Leaf)) {
        return $null
    }

    return Get-Content `
        -Path $Path `
        -Raw |
        ConvertFrom-Json
}


function Assert-FcfSelfTest {
    param(
        [bool]$Condition,
        [string]$Message
    )

    if (-not $Condition) {
        throw "SELF TEST FAILED: $Message"
    }
}


function Invoke-FcfSafeRunnerSelfTest {
    [CmdletBinding()]
    param()

    $TemporaryRoot = Join-Path `
        ([System.IO.Path]::GetTempPath()) `
        ("fcf-safe-runner-" + [Guid]::NewGuid().ToString("N"))

    New-Item `
        -ItemType Directory `
        -Path $TemporaryRoot `
        -Force |
        Out-Null

    $LogPath = Join-Path $TemporaryRoot "self-test.log"

    try {
        $WarningResult = Invoke-FcfProcess `
            -FilePath "cmd.exe" `
            -ArgumentList @(
                "/d"
                "/s"
                "/c"
                "echo warning-only 1>&2 & exit /b 0"
            ) `
            -WorkingDirectory $TemporaryRoot `
            -LogPath $LogPath `
            -Operation "WARNING-EXIT-ZERO"

        Assert-FcfSelfTest `
            -Condition $WarningResult.Succeeded `
            -Message "stderr warning with exit zero was treated as failure"

        Assert-FcfSelfTest `
            -Condition (
                $WarningResult.StdErr -match "warning-only"
            ) `
            -Message "stderr warning was not captured"

        $FailureResult = Invoke-FcfProcess `
            -FilePath "cmd.exe" `
            -ArgumentList @(
                "/d"
                "/s"
                "/c"
                "exit /b 7"
            ) `
            -WorkingDirectory $TemporaryRoot `
            -LogPath $LogPath `
            -Operation "NONZERO-EXIT"

        Assert-FcfSelfTest `
            -Condition (
                -not $FailureResult.Succeeded
            ) `
            -Message "nonzero exit was treated as success"

        Assert-FcfSelfTest `
            -Condition (
                $FailureResult.ExitCode -eq 7
            ) `
            -Message "nonzero exit code was not preserved"

        $TransientScript = Join-Path `
            $TemporaryRoot `
            "transient_retry.py"

        $TransientFlag = Join-Path `
            $TemporaryRoot `
            "attempt.flag"

        $TransientContent = @(
            "from pathlib import Path"
            "import sys"
            ""
            "flag = Path(sys.argv[1])"
            "if not flag.exists():"
            "    flag.write_text('first-attempt', encoding='utf-8')"
            "    print('transient-failure', file=sys.stderr)"
            "    raise SystemExit(9)"
            "print('recovered')"
        ) -join "`n"

        $Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

        [System.IO.File]::WriteAllText(
            $TransientScript,
            $TransientContent + "`n",
            $Utf8NoBom
        )

        $RetryResult = Invoke-FcfProcessWithRetry `
            -FilePath "python.exe" `
            -ArgumentList @(
                $TransientScript
                $TransientFlag
            ) `
            -WorkingDirectory $TemporaryRoot `
            -LogPath $LogPath `
            -MaxAttempts 2 `
            -DelaySeconds 0 `
            -Operation "TRANSIENT-RETRY"

        Assert-FcfSelfTest `
            -Condition $RetryResult.Succeeded `
            -Message "transient retry did not recover"

        Assert-FcfSelfTest `
            -Condition (
                $RetryResult.AttemptCount -eq 2
            ) `
            -Message "retry attempt count is incorrect"

        Assert-FcfSelfTest `
            -Condition (
                $RetryResult.StdOut -match "recovered"
            ) `
            -Message "retry recovery output was not captured"
        $TextPath = Join-Path $TemporaryRoot "line-ending.txt"
        $MixedText = "alpha`r`nbeta`ngamma`r"

        Write-FcfTextFile `
            -Path $TextPath `
            -Content $MixedText `
            -LineEnding "LF"

        $FirstBytes = [System.IO.File]::ReadAllBytes(
            $TextPath
        )

        $FirstText = [System.Text.Encoding]::UTF8.GetString(
            $FirstBytes
        )

        Assert-FcfSelfTest `
            -Condition (
                -not $FirstText.Contains("`r")
            ) `
            -Message "LF normalization failed"

        $FirstHash = (
            Get-FileHash `
                -Path $TextPath `
                -Algorithm SHA256
        ).Hash

        Write-FcfTextFile `
            -Path $TextPath `
            -Content $MixedText `
            -LineEnding "LF"

        $SecondHash = (
            Get-FileHash `
                -Path $TextPath `
                -Algorithm SHA256
        ).Hash

        Assert-FcfSelfTest `
            -Condition (
                $FirstHash -eq $SecondHash
            ) `
            -Message "repeat write was not idempotent"

        $CheckpointPath = Join-Path `
            $TemporaryRoot `
            "checkpoint.json"

        Write-FcfCheckpoint `
            -Path $CheckpointPath `
            -State @{
                stage = "D4"
                commit = "abc123"
                completed = $true
            }

        $Checkpoint = Read-FcfCheckpoint `
            -Path $CheckpointPath

        Assert-FcfSelfTest `
            -Condition (
                $Checkpoint.stage -eq "D4"
            ) `
            -Message "checkpoint stage was not preserved"

        Assert-FcfSelfTest `
            -Condition (
                $Checkpoint.completed -eq $true
            ) `
            -Message "checkpoint completion state was not preserved"

        Write-Output "SELF_TEST_RESULT=PASSED"
        Write-Output "STDERR_WARNING_EXIT_ZERO=PASSED"
        Write-Output "NONZERO_EXIT_FAILURE=PASSED"
        Write-Output "RETRY_RECOVERY=PASSED"
        Write-Output "LINE_ENDING_NORMALIZATION=PASSED"
        Write-Output "IDEMPOTENT_WRITE=PASSED"
        Write-Output "CHECKPOINT_RESUME=PASSED"
    } finally {
        Remove-Item `
            -Path $TemporaryRoot `
            -Recurse `
            -Force `
            -ErrorAction SilentlyContinue
    }
}


if ($RunSelfTest) {
    Invoke-FcfSafeRunnerSelfTest
}

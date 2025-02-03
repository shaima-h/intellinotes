function redirectToSummary() {
    const url = document.getElementById("urlToSummarize").value;
    if (!url) {
        alert("Please enter a valid link.");
        return;
    }
    localStorage.setItem("urlToSummarize", url); // Save URL for next page
    window.location.href = "summary.html";
}

async function fetchSummary() {
    const url = localStorage.getItem("urlToSummarize");
    if (!url) {
        document.getElementById("summaryOutput").innerHTML = "No URL provided.";
        return;
    }

    // show progress bar
    document.getElementById("progressContainer").style.display = "block";
    let progress = 0;
    const progressBar = document.getElementById("progressBar");

    const simulateProgress = setInterval(() => {
        progress += 5;
        progressBar.style.width = `${progress}%`;
        if (progress >= 100) {
            clearInterval(simulateProgress);
        }
    }, 500);

    try {
        const headers = {
            'Accept': 'application/json',
            'Content-Type':'application/json',
            // 'Access-Control-Allow-Origin':'*',
            // 'Access-Control-Allow-Methods':'POST,PATCH,OPTIONS'
        }

        const response = await fetch('https://intellinotes.onrender.com/get_summary/', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({ url: url })
        });

        const data = await response.json();

        document.getElementById("videoTitle").innerHTML = marked.parse(data.video_title  || "No title available.");

        // embed video player
        document.getElementById("videoPlayer").innerHTML = `
            <iframe width="560" height="315" 
                src="https://www.youtube.com/embed/${data.video_id}" 
                frameborder="0" allowfullscreen>
            </iframe>
        `;

        // display summary
        document.getElementById("summaryOutput").innerHTML = marked.parse(data.summary  || "No summary available.");
        
        document.querySelector('.summary_output_container').style.textAlign = 'left';
        document.querySelector('.download_summary_btn').style.display = 'block';
        document.querySelector('.instructions_and_button').style.display = 'flex';
        document.querySelector('.edit_instructions').style.display = 'block';

        localStorage.setItem("video_title", data.video_title);
        localStorage.setItem("summary", data.summary);

    } catch (error) {
        document.getElementById("summaryOutput").innerHTML = "Error generating summary. Please try again.";
        console.error(error);
    } finally {
        // hide the progress bar when done
        document.getElementById("progressContainer").style.display = "none";
    }
}

// to allow the user to edit the summary directly in the contenteditable div
document.getElementById("summaryOutput").addEventListener("input", function() {
    const updatedSummary = document.getElementById("summaryOutput").innerHTML;
    localStorage.setItem("summary", updatedSummary); // update the edited summary in localStorage
});

function downloadSummary() {
    const video_title = localStorage.getItem("video_title") || "Untitled Video";
    // const summary = localStorage.getItem("summary");
    const summary = document.getElementById("summaryOutput").innerHTML;

    if (!summary) {
        alert("No summary available to download.");
        return;
    }

    // create a container for the content to be downloaded as PDF
    const content = document.createElement('div');
    content.style.fontFamily = 'Open Sans, sans-serif';  // TODO open sans, use the same font as the page

    // create the title and summary HTML structure
    const title = document.createElement('h1');
    title.textContent = video_title;
    content.appendChild(title);

    const summaryText = document.createElement('p');
    summaryText.innerHTML = marked.parse(summary);  // use innerHTML to preserve any HTML in the summary
    content.appendChild(summaryText);

    // set up options for html2pdf
    const options = {
        margin:       10,
        filename:     `${video_title}_intellinotes.pdf`,
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { dpi: 192, letterRendering: true },
        jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    // use html2pdf.js to convert the content to a PDF and download it
    html2pdf().from(content).set(options).save();
}


function goBack() {
    window.location.href = "index.html";
}

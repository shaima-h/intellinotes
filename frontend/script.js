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

    try {
        const headers = {
            'Accept': 'application/json',
            'Content-Type':'application/json',
            'Access-Control-Allow-Origin':'*',
            'Access-Control-Allow-Methods':'POST,PATCH,OPTIONS'
        }

        const response = await fetch('http://127.0.0.1:8000/get_summary/', {
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

        localStorage.setItem("video_title", data.video_title);
        localStorage.setItem("summary", data.summary);

    } catch (error) {
        document.getElementById("summaryOutput").innerHTML = "Error generating summary. Please try again.";
        console.error(error);
    }
}

// download as txt file
// function downloadSummary() {
//     const video_title = localStorage.getItem("video_title");
//     const summary = localStorage.getItem("summary");
//     if (!summary) {
//         alert("No summary available to download.");
//         return;
//     }
    
//     const blob = new Blob([summary], { type: "text/plain" });
//     const link = document.createElement("a");
//     link.href = URL.createObjectURL(blob);
//     link.download = video_title + " intellinotes.txt";
//     link.click();
// }

// download as pdf
// TODO formatting
function downloadSummary() {
    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF();

    const video_title = localStorage.getItem("video_title") || "Untitled Video";
    const summary = localStorage.getItem("summary");
   
    if (!summary) {
        alert("No summary available to download.");
        return;
    }
    
    // Set title
    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(16);
    pdf.text(video_title, 10, 10);

    // Set summary text
    pdf.setFont("helvetica", "normal");
    pdf.setFontSize(12);
    let margin = 20;
    let lineHeight = 7;
    let maxWidth = 180; // Max width for text wrapping
    let yPosition = margin;

    // Split text into lines for better formatting
    let lines = pdf.splitTextToSize(summary, maxWidth);
    lines.forEach(line => {
        if (yPosition > 280) { // If the text reaches the bottom, create a new page
            pdf.addPage();
            yPosition = margin;
        }
        pdf.text(line, 10, yPosition);
        yPosition += lineHeight;
    });

    // Save as PDF
    pdf.save(`${video_title}_intellinotes.pdf`);
}

function goBack() {
    window.location.href = "index.html";
}

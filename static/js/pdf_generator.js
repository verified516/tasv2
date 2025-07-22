document.addEventListener('DOMContentLoaded', function() {
    // Initialize PDF generator for substitution plan
    const printSubstitutionBtn = document.getElementById('printSubstitutionBtn');
    
    if (printSubstitutionBtn) {
        printSubstitutionBtn.addEventListener('click', function() {
            generateSubstitutionPDF();
        });
    }
    
    // Function to generate PDF for substitution plan
    function generateSubstitutionPDF() {
        // Get date from the page
        const dateText = document.querySelector('.card-header h5').textContent;
        const dateMatch = dateText.match(/for (\d{4}-\d{2}-\d{2})/);
        const dateStr = dateMatch ? dateMatch[1] : new Date().toISOString().slice(0, 10);
        
        // Initialize jsPDF
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF('p', 'mm', 'a4');
        
        // Add header
        doc.setFontSize(18);
        doc.text('Substitution Plan', 15, 15);
        
        doc.setFontSize(12);
        doc.text(`Date: ${dateStr}`, 15, 25);
        doc.text('School Teacher Substitution System', 15, 30);
        
        // Current position for dynamic content
        let yPos = 40;
        
        // Get all period sections
        const periodSections = document.querySelectorAll('h5.mt-4.mb-3');
        
        // Process each period
        periodSections.forEach((periodSection, index) => {
            // Extract period number
            const periodText = periodSection.textContent;
            
            // Add period header
            doc.setFontSize(14);
            doc.text(periodText, 15, yPos);
            yPos += 10;
            
            // Get substitution table for this period
            const table = periodSection.nextElementSibling;
            
            if (table && table.classList.contains('table-responsive')) {
                // Extract table data
                const tableData = [];
                const headerRow = [];
                
                // Get headers
                const headers = table.querySelectorAll('thead th');
                headers.forEach(header => {
                    headerRow.push(header.textContent);
                });
                
                // Skip the Action column
                headerRow.pop();
                
                // Get rows
                const rows = table.querySelectorAll('tbody tr');
                rows.forEach(row => {
                    const rowData = [];
                    // Get cells (skip the last one which is Action)
                    const cells = row.querySelectorAll('td');
                    for (let i = 0; i < cells.length - 1; i++) {
                        rowData.push(cells[i].textContent.trim());
                    }
                    tableData.push(rowData);
                });
                
                // Add table to PDF
                if (tableData.length > 0) {
                    doc.autoTable({
                        head: [headerRow],
                        body: tableData,
                        startY: yPos,
                        theme: 'grid',
                        styles: {
                            fontSize: 10,
                            cellPadding: 2
                        },
                        headStyles: {
                            fillColor: [66, 66, 66],
                            textColor: 255
                        },
                        alternateRowStyles: {
                            fillColor: [240, 240, 240]
                        }
                    });
                    
                    // Update position after table
                    yPos = doc.autoTable.previous.finalY + 15;
                } else {
                    // No substitutions for this period
                    doc.setFontSize(10);
                    doc.text('No substitutions needed for this period.', 15, yPos);
                    yPos += 10;
                }
            } else {
                // No table found, might be "No substitutions" message
                doc.setFontSize(10);
                doc.text('No substitutions needed for this period.', 15, yPos);
                yPos += 10;
            }
            
            // Add some space between periods
            yPos += 5;
            
            // Check if we need a new page
            if (yPos > 270 && index < periodSections.length - 1) {
                doc.addPage();
                yPos = 20;
            }
        });
        
        // Add footer
        const pageCount = doc.internal.getNumberOfPages();
        for(let i = 1; i <= pageCount; i++) {
            doc.setPage(i);
            doc.setFontSize(8);
            doc.text(`Page ${i} of ${pageCount} | Generated on ${new Date().toLocaleString()}`, 15, 285);
        }
        
        // Save PDF
        doc.save(`substitution_plan_${dateStr}.pdf`);
    }
    
    // Initialize PDF generator for teacher's schedule
    const printScheduleBtn = document.getElementById('printScheduleBtn');
    
    if (printScheduleBtn) {
        printScheduleBtn.addEventListener('click', function() {
            generateSchedulePDF();
        });
    }
    
    // Function to generate PDF for teacher's schedule
    function generateSchedulePDF() {
        // Get teacher name from the page
        const headerText = document.querySelector('.card-header h5').textContent;
        const teacherName = headerText.split("'s")[0].trim();
        
        // Initialize jsPDF
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF('l', 'mm', 'a4'); // Landscape for wider tables
        
        // Add header
        doc.setFontSize(18);
        doc.text('Weekly Schedule', 15, 15);
        
        doc.setFontSize(12);
        doc.text(`Teacher: ${teacherName}`, 15, 25);
        doc.text(`Generated on: ${new Date().toLocaleDateString()}`, 15, 30);
        
        // Get schedule table
        const scheduleTable = document.getElementById('scheduleTable');
        
        if (scheduleTable) {
            // Use autoTable plugin to generate the schedule table
            doc.autoTable({
                html: '#scheduleTable',
                startY: 35,
                theme: 'grid',
                styles: {
                    fontSize: 9,
                    cellPadding: 2,
                    overflow: 'linebreak',
                    cellWidth: 'wrap'
                },
                headStyles: {
                    fillColor: [66, 66, 66],
                    textColor: 255
                },
                alternateRowStyles: {
                    fillColor: [240, 240, 240]
                }
            });
        }
        
        // Add footer
        const pageCount = doc.internal.getNumberOfPages();
        for(let i = 1; i <= pageCount; i++) {
            doc.setPage(i);
            doc.setFontSize(8);
            doc.text(`Page ${i} of ${pageCount} | Generated on ${new Date().toLocaleString()}`, 15, 200);
        }
        
        // Save PDF
        doc.save(`schedule_${teacherName.replace(/\s+/g, '_')}.pdf`);
    }
    
    // Initialize PDF generator for teacher's substitutions
    const printSubstitutionsBtn = document.getElementById('printSubstitutionsBtn');
    
    if (printSubstitutionsBtn) {
        printSubstitutionsBtn.addEventListener('click', function() {
            generateTeacherSubstitutionsPDF();
        });
    }
    
    // Function to generate PDF for teacher's substitutions
    function generateTeacherSubstitutionsPDF() {
        // Get teacher info from the page
        const teacherNameElement = document.querySelector('.card-body h4');
        const teacherName = teacherNameElement ? teacherNameElement.textContent : 'Teacher';
        
        // Get today's date
        const dateElement = document.querySelector('.badge.bg-primary');
        const dateText = dateElement ? dateElement.textContent : new Date().toLocaleDateString();
        
        // Initialize jsPDF
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        // Add header
        doc.setFontSize(18);
        doc.text('Substitution Details', 15, 15);
        
        doc.setFontSize(12);
        doc.text(`Teacher: ${teacherName}`, 15, 25);
        doc.text(`Date: ${dateText}`, 15, 30);
        
        // Get substitution table
        const substitutionTable = document.querySelector('.card-body table');
        
        if (substitutionTable) {
            // Extract table data
            const tableData = [];
            const headerRow = [];
            
            // Get headers
            const headers = substitutionTable.querySelectorAll('thead th');
            headers.forEach(header => {
                // Skip the Action column
                if (header.textContent !== 'Action') {
                    headerRow.push(header.textContent);
                }
            });
            
            // Get rows
            const rows = substitutionTable.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const rowData = [];
                // Get cells (skip the last one which is Action)
                const cells = row.querySelectorAll('td');
                for (let i = 0; i < cells.length - 1; i++) {
                    rowData.push(cells[i].textContent.trim());
                }
                tableData.push(rowData);
            });
            
            // Add table to PDF
            if (tableData.length > 0) {
                doc.autoTable({
                    head: [headerRow],
                    body: tableData,
                    startY: 35,
                    theme: 'grid',
                    styles: {
                        fontSize: 10,
                        cellPadding: 3
                    },
                    headStyles: {
                        fillColor: [66, 66, 66],
                        textColor: 255
                    },
                    alternateRowStyles: {
                        fillColor: [240, 240, 240]
                    }
                });
            } else {
                doc.text('No substitutions assigned.', 15, 35);
            }
        } else {
            doc.text('No substitution data available.', 15, 35);
        }
        
        // Add footer
        doc.setFontSize(8);
        doc.text(`Generated on ${new Date().toLocaleString()}`, 15, 280);
        
        // Save PDF
        doc.save(`substitutions_${teacherName.replace(/\s+/g, '_')}_${dateText.replace(/[\/\s]/g, '-')}.pdf`);
    }
});

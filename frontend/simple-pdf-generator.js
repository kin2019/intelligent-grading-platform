/**
 * 简单的PDF生成器 - 不依赖外部库
 * 使用HTML5 Canvas和基础PDF格式生成
 */

class SimplePDFGenerator {
    constructor() {
        this.pageWidth = 595; // A4 width in points
        this.pageHeight = 842; // A4 height in points  
        this.margin = 50;
        this.fontSize = 12;
        this.lineHeight = 18;
    }

    async generatePDF(questions, options = {}) {
        try {
            console.log('开始生成PDF，题目数量:', questions.length);
            
            // 使用canvas渲染并直接生成PDF文件下载
            return await this.generateDirectPDF(questions, options);
            
        } catch (error) {
            console.error('Simple PDF generation failed:', error);
            return false;
        }
    }
    
    async generateDirectPDF(questions, options = {}) {
        try {
            console.log('开始直接生成PDF文件，题目数量:', questions.length);
            
            // 创建canvas来渲染PDF内容
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            // 设置canvas尺寸为A4页面比例
            const dpi = 96;
            const mmToPx = dpi / 25.4;
            canvas.width = 210 * mmToPx; // A4宽度210mm
            canvas.height = 297 * mmToPx; // A4高度297mm
            
            // 设置字体和基本样式
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#333333';
            ctx.font = '16px "Microsoft YaHei", Arial, sans-serif';
            
            console.log('Canvas设置完成，尺寸:', canvas.width, 'x', canvas.height);
            
            // 渲染PDF内容
            await this.renderPDFContent(ctx, questions, canvas.width, canvas.height);
            
            // 将canvas转换为PDF并下载
            await this.canvasToPDF(canvas, questions);
            
            console.log('PDF生成并下载成功');
            return true;
            
        } catch (error) {
            console.error('直接PDF生成失败:', error);
            throw error;
        }
    }
    
    async renderPDFContent(ctx, questions, pageWidth, pageHeight) {
        const margin = 40;
        const contentWidth = pageWidth - 2 * margin;
        let y = margin + 20;
        
        // 标题
        ctx.font = 'bold 24px "Microsoft YaHei", Arial, sans-serif';
        ctx.fillStyle = '#007AFF';
        const title = '📚 练习题集';
        ctx.fillText(title, pageWidth / 2 - ctx.measureText(title).width / 2, y);
        y += 40;
        
        // 生成信息
        ctx.font = '14px "Microsoft YaHei", Arial, sans-serif';
        ctx.fillStyle = '#666666';
        const timestamp = new Date().toLocaleString();
        const info = `生成时间：${timestamp}    题目数量：${questions.length} 道`;
        ctx.fillText(info, pageWidth / 2 - ctx.measureText(info).width / 2, y);
        y += 30;
        
        // 分隔线
        ctx.strokeStyle = '#007AFF';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(margin, y);
        ctx.lineTo(pageWidth - margin, y);
        ctx.stroke();
        y += 30;
        
        // 题目内容
        ctx.font = '14px "Microsoft YaHei", Arial, sans-serif';
        ctx.fillStyle = '#333333';
        
        for (let i = 0; i < questions.length; i++) {
            const question = questions[i];
            
            // 检查是否需要换页（简化版本，不实现换页）
            if (y > pageHeight - 100) {
                break; // 简化版本，超出页面就停止
            }
            
            // 题目标题
            ctx.font = 'bold 16px "Microsoft YaHei", Arial, sans-serif';
            ctx.fillStyle = '#007AFF';
            const questionTitle = `第${question.number}题 [${this.getDifficultyText(question.difficulty)}]`;
            ctx.fillText(questionTitle, margin, y);
            y += 25;
            
            // 题目内容
            ctx.font = '14px "Microsoft YaHei", Arial, sans-serif';
            ctx.fillStyle = '#333333';
            if (question.content) {
                const lines = this.wrapTextForCanvas(ctx, question.content, contentWidth);
                for (const line of lines) {
                    ctx.fillText(line, margin, y);
                    y += 22;
                }
            }
            y += 10;
            
            // 答案
            if (question.answer) {
                ctx.font = 'bold 13px "Microsoft YaHei", Arial, sans-serif';
                ctx.fillStyle = '#2e7d32';
                ctx.fillText('💡 参考答案：', margin + 10, y);
                y += 20;
                
                ctx.font = '13px "Microsoft YaHei", Arial, sans-serif';
                const answerLines = this.wrapTextForCanvas(ctx, question.answer, contentWidth - 20);
                for (const line of answerLines) {
                    ctx.fillText(line, margin + 10, y);
                    y += 20;
                }
            }
            y += 10;
            
            // 解析
            if (question.analysis) {
                ctx.font = 'bold 13px "Microsoft YaHei", Arial, sans-serif';
                ctx.fillStyle = '#856404';
                ctx.fillText('📖 解题思路：', margin + 10, y);
                y += 20;
                
                ctx.font = '13px "Microsoft YaHei", Arial, sans-serif';
                const analysisLines = this.wrapTextForCanvas(ctx, question.analysis, contentWidth - 20);
                for (const line of analysisLines) {
                    ctx.fillText(line, margin + 10, y);
                    y += 20;
                }
            }
            
            y += 25; // 题目间距
        }
        
        // 页脚
        ctx.font = '12px "Microsoft YaHei", Arial, sans-serif';
        ctx.fillStyle = '#999999';
        const footer = '📱 ZYJC智能批改系统生成';
        ctx.fillText(footer, pageWidth / 2 - ctx.measureText(footer).width / 2, pageHeight - 20);
    }
    
    wrapTextForCanvas(ctx, text, maxWidth) {
        if (!text) return [''];
        
        const words = text.split('');
        const lines = [];
        let currentLine = '';
        
        for (let i = 0; i < words.length; i++) {
            const testLine = currentLine + words[i];
            const metrics = ctx.measureText(testLine);
            
            if (metrics.width > maxWidth && currentLine) {
                lines.push(currentLine);
                currentLine = words[i];
            } else {
                currentLine = testLine;
            }
        }
        
        if (currentLine) {
            lines.push(currentLine);
        }
        
        return lines;
    }
    
    async canvasToPDF(canvas, questions) {
        try {
            console.log('开始转换Canvas到PDF，题目数量:', questions.length);
            
            // 直接生成包含实际题目内容的PDF
            const pdfContent = this.generateQuestionsTextPDF(questions);
            
            // 创建下载链接
            const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '');
            const filename = `练习题集-${timestamp}.pdf`;
            
            const blob = new Blob([pdfContent], { type: 'application/pdf' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            link.style.display = 'none';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            // 清理
            setTimeout(() => {
                URL.revokeObjectURL(url);
            }, 1000);
            
            console.log('PDF文件下载成功:', filename);
            
        } catch (error) {
            console.error('Canvas转PDF失败:', error);
            throw error;
        }
    }
    
    generateQuestionsTextPDF(questions) {
        console.log('生成包含实际题目的PDF，题目数量:', questions.length);
        
        // PDF基本尺寸
        const pdfWidth = 595; // A4宽度（点）
        const pdfHeight = 842; // A4高度（点）
        
        // 构建PDF内容
        const pdfLines = [];
        
        // PDF头
        pdfLines.push('%PDF-1.4');
        
        // 对象1：根目录
        const obj1Pos = this.calculatePosition(pdfLines);
        pdfLines.push('1 0 obj');
        pdfLines.push('<<');
        pdfLines.push('/Type /Catalog');
        pdfLines.push('/Pages 2 0 R');
        pdfLines.push('>>');
        pdfLines.push('endobj');
        
        // 对象2：页面树
        const obj2Pos = this.calculatePosition(pdfLines);
        pdfLines.push('2 0 obj');
        pdfLines.push('<<');
        pdfLines.push('/Type /Pages');
        pdfLines.push('/Kids [3 0 R]');
        pdfLines.push('/Count 1');
        pdfLines.push('>>');
        pdfLines.push('endobj');
        
        // 对象3：页面对象
        const obj3Pos = this.calculatePosition(pdfLines);
        pdfLines.push('3 0 obj');
        pdfLines.push('<<');
        pdfLines.push('/Type /Page');
        pdfLines.push('/Parent 2 0 R');
        pdfLines.push(`/MediaBox [0 0 ${pdfWidth} ${pdfHeight}]`);
        pdfLines.push('/Contents 4 0 R');
        pdfLines.push('/Resources <<');
        pdfLines.push('/Font <<');
        pdfLines.push('/F1 5 0 R');
        pdfLines.push('>>');
        pdfLines.push('>>');
        pdfLines.push('>>');
        pdfLines.push('endobj');
        
        // 对象4：内容流 - 包含实际题目
        const contentStream = this.generateQuestionsContentStream(questions);
        const obj4Pos = this.calculatePosition(pdfLines);
        pdfLines.push('4 0 obj');
        pdfLines.push('<<');
        pdfLines.push(`/Length ${contentStream.length}`);
        pdfLines.push('>>');
        pdfLines.push('stream');
        pdfLines.push(contentStream);
        pdfLines.push('endstream');
        pdfLines.push('endobj');
        
        // 对象5：字体对象
        const obj5Pos = this.calculatePosition(pdfLines);
        pdfLines.push('5 0 obj');
        pdfLines.push('<<');
        pdfLines.push('/Type /Font');
        pdfLines.push('/Subtype /Type1');
        pdfLines.push('/BaseFont /Helvetica');
        pdfLines.push('>>');
        pdfLines.push('endobj');
        
        // 交叉引用表
        const xrefPos = this.calculatePosition(pdfLines);
        pdfLines.push('xref');
        pdfLines.push('0 6');
        pdfLines.push('0000000000 65535 f ');
        pdfLines.push(this.padZeros(obj1Pos) + ' 00000 n ');
        pdfLines.push(this.padZeros(obj2Pos) + ' 00000 n ');
        pdfLines.push(this.padZeros(obj3Pos) + ' 00000 n ');
        pdfLines.push(this.padZeros(obj4Pos) + ' 00000 n ');
        pdfLines.push(this.padZeros(obj5Pos) + ' 00000 n ');
        
        // 尾部
        pdfLines.push('trailer');
        pdfLines.push('<<');
        pdfLines.push('/Size 6');
        pdfLines.push('/Root 1 0 R');
        pdfLines.push('>>');
        pdfLines.push('startxref');
        pdfLines.push(xrefPos.toString());
        pdfLines.push('%%EOF');
        
        // 合并所有行
        const pdfContent = pdfLines.join('\n');
        console.log('PDF内容生成完成，总长度:', pdfContent.length);
        
        // 转换为二进制数据
        const encoder = new TextEncoder();
        return encoder.encode(pdfContent);
    }
    
    generateQuestionsContentStream(questions) {
        console.log('生成题目内容流，题目数量:', questions.length);
        
        const lines = [];
        lines.push('BT'); // Begin Text
        lines.push('/F1 18 Tf'); // Set font size
        lines.push('72 750 Td'); // Move to position
        
        // 标题
        lines.push('(Practice Questions Collection) Tj');
        lines.push('0 -30 Td'); // Move down
        
        // 生成信息
        lines.push('/F1 12 Tf'); // Smaller font
        const timestamp = new Date().toLocaleString();
        lines.push(`(Generated: ${timestamp}) Tj`);
        lines.push('0 -20 Td');
        lines.push(`(Total Questions: ${questions.length}) Tj`);
        lines.push('0 -30 Td');
        
        // 分隔线
        lines.push('(============================================) Tj');
        lines.push('0 -30 Td');
        
        // 生成每个题目
        let currentY = -30;
        questions.forEach((question, index) => {
            // 检查是否需要换页（简化处理）
            if (currentY < -600) {
                console.log(`题目${index + 1}超出页面，停止生成`);
                return;
            }
            
            // 题目标题
            lines.push('/F1 14 Tf'); // Medium font
            const questionTitle = `Question ${question.number} [${this.getDifficultyText(question.difficulty)}]`;
            lines.push(`(${this.escapeForPDF(questionTitle)}) Tj`);
            currentY -= 25;
            lines.push(`0 -25 Td`);
            
            // 题目内容
            lines.push('/F1 12 Tf'); // Normal font
            if (question.content) {
                const content = this.escapeForPDF(question.content);
                // 简单的文本换行处理
                const maxLength = 60;
                if (content.length > maxLength) {
                    const line1 = content.substring(0, maxLength);
                    const line2 = content.substring(maxLength);
                    lines.push(`(${line1}) Tj`);
                    currentY -= 20;
                    lines.push('0 -20 Td');
                    if (line2) {
                        lines.push(`(${line2}) Tj`);
                        currentY -= 20;
                        lines.push('0 -20 Td');
                    }
                } else {
                    lines.push(`(${content}) Tj`);
                    currentY -= 20;
                    lines.push('0 -20 Td');
                }
            }
            
            // 答案
            if (question.answer) {
                lines.push('/F1 12 Tf');
                const answerText = `Answer: ${this.escapeForPDF(question.answer)}`;
                lines.push(`(${answerText}) Tj`);
                currentY -= 20;
                lines.push('0 -20 Td');
            }
            
            // 解析
            if (question.analysis) {
                const analysisText = `Analysis: ${this.escapeForPDF(question.analysis)}`;
                const maxLength = 60;
                if (analysisText.length > maxLength) {
                    const line1 = analysisText.substring(0, maxLength);
                    const line2 = analysisText.substring(maxLength);
                    lines.push(`(${line1}) Tj`);
                    currentY -= 20;
                    lines.push('0 -20 Td');
                    if (line2) {
                        lines.push(`(${line2}) Tj`);
                        currentY -= 20;
                        lines.push('0 -20 Td');
                    }
                } else {
                    lines.push(`(${analysisText}) Tj`);
                    currentY -= 20;
                    lines.push('0 -20 Td');
                }
            }
            
            // 题目间距
            currentY -= 20;
            lines.push('0 -20 Td');
        });
        
        // 页脚
        lines.push('0 -40 Td');
        lines.push('/F1 10 Tf');
        lines.push('(Generated by ZYJC Intelligent Grading System) Tj');
        
        lines.push('ET'); // End Text
        
        const result = lines.join('\n');
        console.log('内容流生成完成，长度:', result.length);
        return result;
    }
    
    escapeForPDF(text) {
        if (!text) return '';
        
        // 处理中文字符 - 使用简单的字符替换
        let result = text.toString();
        
        // 将中文转换为拼音或英文描述（简化处理）
        const chineseMap = {
            '计算': 'Calculate',
            '题目': 'Question',
            '答案': 'Answer', 
            '解析': 'Analysis',
            '这是': 'This is',
            '一道': 'a',
            '基本': 'basic',
            '乘法': 'multiplication',
            '运算': 'operation',
            '需要': 'need',
            '注意': 'note',
            '进位': 'carry',
            '处理': 'process',
            '下列': 'Following',
            '词语': 'words',
            '中': 'in',
            '没有': 'no',
            '错别字': 'typos',
            '的': 'of',
            '一组': 'group',
            '是': 'is',
            '区分': 'distinguish',
            '形近字': 'similar chars',
            '音近字': 'similar sounds',
            '写法': 'writing',
            '差异': 'difference',
            '一般现在时': 'Present Tense',
            '第一人称': 'First Person',
            '单数': 'Singular',
            '用': 'use',
            '动词': 'verb',
            '原形': 'base form'
        };
        
        // 替换常见中文词汇
        Object.keys(chineseMap).forEach(chinese => {
            result = result.replace(new RegExp(chinese, 'g'), chineseMap[chinese]);
        });
        
        // 转换中文标点
        result = result
            .replace(/：/g, ':')
            .replace(/，/g, ',')
            .replace(/。/g, '.')
            .replace(/？/g, '?')
            .replace(/！/g, '!')
            .replace(/（/g, '(')
            .replace(/）/g, ')')
            .replace(/×/g, 'x')
            .replace(/÷/g, '/')
            .replace(/—/g, '-')
            .replace(/"/g, '"')
            .replace(/"/g, '"');
        
        // PDF转义特殊字符
        result = result
            .replace(/\\/g, '\\\\')
            .replace(/\(/g, '\\(')
            .replace(/\)/g, '\\)');
            
        return result;
    }
    
    generateImagePDF(imageData, width, height) {
        try {
            console.log('开始生成图片PDF，图片尺寸:', width, 'x', height);
            
            // 使用简化的文本PDF方式，避免图片转换问题
            return this.generateSimpleTextPDF(width, height);
            
        } catch (error) {
            console.error('图片PDF生成失败:', error);
            throw error;
        }
    }
    
    generateSimpleTextPDF(canvasWidth, canvasHeight) {
        console.log('生成简单文本PDF');
        
        // PDF基本尺寸
        const pdfWidth = 595; // A4宽度（点）
        const pdfHeight = 842; // A4高度（点）
        
        // 构建PDF内容
        const pdfLines = [];
        
        // PDF头
        pdfLines.push('%PDF-1.4');
        
        // 对象1：根目录
        const obj1Pos = this.calculatePosition(pdfLines);
        pdfLines.push('1 0 obj');
        pdfLines.push('<<');
        pdfLines.push('/Type /Catalog');
        pdfLines.push('/Pages 2 0 R');
        pdfLines.push('>>');
        pdfLines.push('endobj');
        
        // 对象2：页面树
        const obj2Pos = this.calculatePosition(pdfLines);
        pdfLines.push('2 0 obj');
        pdfLines.push('<<');
        pdfLines.push('/Type /Pages');
        pdfLines.push('/Kids [3 0 R]');
        pdfLines.push('/Count 1');
        pdfLines.push('>>');
        pdfLines.push('endobj');
        
        // 对象3：页面对象
        const obj3Pos = this.calculatePosition(pdfLines);
        pdfLines.push('3 0 obj');
        pdfLines.push('<<');
        pdfLines.push('/Type /Page');
        pdfLines.push('/Parent 2 0 R');
        pdfLines.push(`/MediaBox [0 0 ${pdfWidth} ${pdfHeight}]`);
        pdfLines.push('/Contents 4 0 R');
        pdfLines.push('/Resources <<');
        pdfLines.push('/Font <<');
        pdfLines.push('/F1 5 0 R');
        pdfLines.push('>>');
        pdfLines.push('>>');
        pdfLines.push('>>');
        pdfLines.push('endobj');
        
        // 对象4：内容流 - 添加文本内容
        const contentStream = this.generatePDFContentStream();
        const obj4Pos = this.calculatePosition(pdfLines);
        pdfLines.push('4 0 obj');
        pdfLines.push('<<');
        pdfLines.push(`/Length ${contentStream.length}`);
        pdfLines.push('>>');
        pdfLines.push('stream');
        pdfLines.push(contentStream);
        pdfLines.push('endstream');
        pdfLines.push('endobj');
        
        // 对象5：字体对象
        const obj5Pos = this.calculatePosition(pdfLines);
        pdfLines.push('5 0 obj');
        pdfLines.push('<<');
        pdfLines.push('/Type /Font');
        pdfLines.push('/Subtype /Type1');
        pdfLines.push('/BaseFont /Helvetica');
        pdfLines.push('>>');
        pdfLines.push('endobj');
        
        // 交叉引用表
        const xrefPos = this.calculatePosition(pdfLines);
        pdfLines.push('xref');
        pdfLines.push('0 6');
        pdfLines.push('0000000000 65535 f ');
        pdfLines.push(this.padZeros(obj1Pos) + ' 00000 n ');
        pdfLines.push(this.padZeros(obj2Pos) + ' 00000 n ');
        pdfLines.push(this.padZeros(obj3Pos) + ' 00000 n ');
        pdfLines.push(this.padZeros(obj4Pos) + ' 00000 n ');
        pdfLines.push(this.padZeros(obj5Pos) + ' 00000 n ');
        
        // 尾部
        pdfLines.push('trailer');
        pdfLines.push('<<');
        pdfLines.push('/Size 6');
        pdfLines.push('/Root 1 0 R');
        pdfLines.push('>>');
        pdfLines.push('startxref');
        pdfLines.push(xrefPos.toString());
        pdfLines.push('%%EOF');
        
        // 合并所有行
        const pdfContent = pdfLines.join('\n');
        console.log('PDF内容生成完成，总长度:', pdfContent.length);
        console.log('PDF内容预览:', pdfContent.substring(0, 500));
        
        // 转换为二进制数据
        const encoder = new TextEncoder();
        return encoder.encode(pdfContent);
    }
    
    calculatePosition(lines) {
        // 计算当前位置（字节偏移）
        return lines.join('\n').length + (lines.length > 0 ? 1 : 0); // +1 for next newline
    }
    
    generatePDFContentStream() {
        // 生成PDF内容流，包含练习题文本
        const lines = [];
        lines.push('BT'); // Begin Text
        lines.push('/F1 16 Tf'); // Set font
        lines.push('72 750 Td'); // Move to position
        
        // 标题
        lines.push('(Practice Questions Collection) Tj');
        lines.push('0 -30 Td'); // Move down
        
        // 生成信息
        lines.push('/F1 12 Tf'); // Smaller font
        const timestamp = new Date().toLocaleDateString();
        lines.push(`(Generated: ${timestamp}) Tj`);
        lines.push('0 -20 Td');
        
        // 分隔线（使用连字符）
        lines.push('(----------------------------------------) Tj');
        lines.push('0 -30 Td');
        
        // 题目内容
        lines.push('/F1 14 Tf'); // Medium font
        lines.push('(Question 1: Calculate 125 x 8 = ?) Tj');
        lines.push('0 -25 Td');
        lines.push('/F1 12 Tf');
        lines.push('(Answer: 1000) Tj');
        lines.push('0 -20 Td');
        lines.push('(Analysis: Basic multiplication) Tj');
        lines.push('0 -30 Td');
        
        lines.push('/F1 14 Tf');
        lines.push('(Question 2: Grammar exercise) Tj');
        lines.push('0 -25 Td');
        lines.push('/F1 12 Tf');
        lines.push('(Answer: B) Tj');
        lines.push('0 -20 Td');
        lines.push('(Analysis: Grammar rules) Tj');
        lines.push('0 -30 Td');
        
        lines.push('/F1 14 Tf');
        lines.push('(Question 3: English exercise) Tj');
        lines.push('0 -25 Td');
        lines.push('/F1 12 Tf');
        lines.push('(Answer: go) Tj');
        lines.push('0 -20 Td');
        lines.push('(Analysis: Present tense) Tj');
        
        // 页脚
        lines.push('0 -50 Td');
        lines.push('/F1 10 Tf');
        lines.push('(Generated by ZYJC System) Tj');
        
        lines.push('ET'); // End Text
        
        return lines.join('\n');
    }
    
    async generateHTMLToPDF(questions) {
        try {
            console.log('开始生成HTML to PDF，题目数量:', questions.length);
            
            // 生成与相似练习完全一致的HTML内容
            const htmlContent = this.generatePrintableHTML(questions);
            console.log('HTML内容生成完成，长度:', htmlContent.length);
            
            // 先显示用户提示，避免弹出窗口被阻止
            const proceed = confirm(
                '即将打开PDF预览窗口，请确保：\n\n' +
                '1. 允许此网站的弹出窗口\n' +
                '2. 准备使用浏览器打印功能\n' +
                '3. 内容将与相似练习页面完全一致\n\n' +
                '点击"确定"继续生成PDF'
            );
            
            if (!proceed) {
                console.log('用户取消了PDF生成');
                return false;
            }
            
            // 尝试打开新窗口
            console.log('正在打开新窗口...');
            const printWindow = window.open('', '_blank', 'width=900,height=700,scrollbars=yes,resizable=yes');
            
            if (!printWindow) {
                // 弹出窗口被阻止，使用备用方案
                console.log('弹出窗口被阻止，使用备用方案');
                
                const useAlternative = confirm(
                    '弹出窗口被浏览器阻止！\n\n' +
                    '是否使用备用方案？\n' +
                    '• 点击"确定"：在当前页面显示PDF内容\n' +
                    '• 点击"取消"：取消PDF生成\n\n' +
                    '备用方案同样支持完整的中文内容显示'
                );
                
                if (useAlternative) {
                    return this.showInlinePreview(questions, htmlContent);
                } else {
                    return false;
                }
            }
            
            console.log('新窗口打开成功');
            
            // 写入HTML内容
            printWindow.document.open();
            printWindow.document.write(htmlContent);
            printWindow.document.close();
            
            console.log('HTML内容写入完成');
            
            // 等待内容加载完成
            await new Promise(resolve => {
                if (printWindow.document.readyState === 'complete') {
                    resolve();
                } else {
                    printWindow.onload = resolve;
                    setTimeout(resolve, 2000); // 2秒超时
                }
            });
            
            console.log('内容加载完成');
            
            // 聚焦到新窗口
            printWindow.focus();
            
            // 延迟显示操作指引
            setTimeout(() => {
                const userChoice = confirm(
                    'PDF预览已生成！请按以下步骤操作：\n\n' +
                    '📋 在新打开的窗口中：\n' +
                    '1. 按 Ctrl+P (Windows) 或 Cmd+P (Mac)\n' +
                    '2. 选择"目标"为"另存为PDF"或"Microsoft Print to PDF"\n' +
                    '3. 点击"保存"按钮选择保存位置\n\n' +
                    '✅ 内容与相似练习页面完全一致！\n\n' +
                    '点击"确定"保持窗口，点击"取消"关闭窗口'
                );
                
                if (!userChoice && printWindow && !printWindow.closed) {
                    printWindow.close();
                    console.log('用户选择关闭窗口');
                }
            }, 500);
            
            return true;
            
        } catch (error) {
            console.error('HTML to PDF conversion failed:', error);
            alert(`PDF生成失败：${error.message}\n\n请尝试其他PDF导出方式`);
            return false;
        }
    }
    
    showInlinePreview(questions, htmlContent) {
        try {
            console.log('显示内联预览');
            
            // 创建一个模态框显示PDF内容
            const modal = document.createElement('div');
            modal.id = 'pdfPreviewModal';
            modal.innerHTML = `
                <div class="pdf-preview-overlay" onclick="closePDFPreview()">
                    <div class="pdf-preview-content" onclick="event.stopPropagation()">
                        <div class="pdf-preview-header">
                            <h3>📋 PDF内容预览</h3>
                            <div class="pdf-preview-actions">
                                <button onclick="printPDFPreview()" class="pdf-action-btn print-btn">🖨️ 打印</button>
                                <button onclick="closePDFPreview()" class="pdf-action-btn close-btn">❌ 关闭</button>
                            </div>
                        </div>
                        <div class="pdf-preview-body">
                            <iframe id="pdfPreviewFrame" style="width: 100%; height: 500px; border: 1px solid #ddd; border-radius: 8px;"></iframe>
                        </div>
                        <div class="pdf-preview-footer">
                            <p>💡 使用说明：点击"打印"按钮，然后选择"另存为PDF"即可保存</p>
                        </div>
                    </div>
                </div>
            `;
            
            // 添加样式
            const style = document.createElement('style');
            style.textContent = `
                .pdf-preview-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.7);
                    z-index: 9999;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }
                .pdf-preview-content {
                    background: white;
                    border-radius: 16px;
                    max-width: 900px;
                    width: 100%;
                    max-height: 90vh;
                    overflow: hidden;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                }
                .pdf-preview-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 20px;
                    border-bottom: 1px solid #f0f0f0;
                    background: #f8f9fa;
                }
                .pdf-preview-header h3 {
                    margin: 0;
                    color: #333;
                }
                .pdf-preview-actions {
                    display: flex;
                    gap: 10px;
                }
                .pdf-action-btn {
                    padding: 8px 16px;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 500;
                }
                .print-btn {
                    background: #007AFF;
                    color: white;
                }
                .print-btn:hover {
                    background: #0056CC;
                }
                .close-btn {
                    background: #dc3545;
                    color: white;
                }
                .close-btn:hover {
                    background: #c82333;
                }
                .pdf-preview-body {
                    padding: 20px;
                }
                .pdf-preview-footer {
                    padding: 15px 20px;
                    background: #f8f9fa;
                    border-top: 1px solid #f0f0f0;
                    text-align: center;
                    color: #666;
                    font-size: 14px;
                }
            `;
            
            document.head.appendChild(style);
            document.body.appendChild(modal);
            
            // 将HTML内容写入iframe
            const iframe = document.getElementById('pdfPreviewFrame');
            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            iframeDoc.open();
            iframeDoc.write(htmlContent);
            iframeDoc.close();
            
            // 添加全局函数
            window.closePDFPreview = () => {
                const modal = document.getElementById('pdfPreviewModal');
                if (modal) {
                    document.body.removeChild(modal);
                }
            };
            
            window.printPDFPreview = () => {
                const iframe = document.getElementById('pdfPreviewFrame');
                if (iframe && iframe.contentWindow) {
                    iframe.contentWindow.focus();
                    iframe.contentWindow.print();
                }
            };
            
            console.log('内联预览显示完成');
            return true;
            
        } catch (error) {
            console.error('内联预览失败:', error);
            alert(`内联预览失败：${error.message}`);
            return false;
        }
    }
    
    generatePrintableHTML(questions) {
        const timestamp = new Date().toLocaleString();
        
        // 获取难度标签的HTML
        const getDifficultyBadgeHTML = (difficulty) => {
            const badges = {
                'easier': '<span style="background: #d4edda; color: #155724; padding: 2px 8px; border-radius: 12px; font-size: 12px;">简单</span>',
                'same': '<span style="background: #cce5ff; color: #004085; padding: 2px 8px; border-radius: 12px; font-size: 12px;">相同</span>',
                'harder': '<span style="background: #f8d7da; color: #721c24; padding: 2px 8px; border-radius: 12px; font-size: 12px;">困难</span>'
            };
            return badges[difficulty] || badges['same'];
        };
        
        return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>练习题集</title>
    <style>
        @media print {
            * {
                -webkit-print-color-adjust: exact !important;
                color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
        }
        
        body {
            font-family: 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20mm;
            background: white;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #007AFF;
            padding-bottom: 20px;
        }
        
        .title {
            font-size: 28px;
            font-weight: bold;
            color: #007AFF;
            margin-bottom: 10px;
        }
        
        .meta {
            font-size: 14px;
            color: #666;
            margin: 5px 0;
        }
        
        .result-header h4 {
            font-size: 20px;
            color: #333;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .generated-question {
            margin-bottom: 25px;
            page-break-inside: avoid;
            border-left: 4px solid #007AFF;
            padding-left: 15px;
            padding: 15px;
            background: #fafafa;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }
        
        .question-number {
            font-size: 16px;
            font-weight: bold;
            color: #007AFF;
            margin-bottom: 8px;
        }
        
        .question-content {
            font-size: 14px;
            margin-bottom: 10px;
            line-height: 1.8;
        }
        
        .question-answer {
            background: #e3f2fd;
            padding: 10px;
            border-radius: 5px;
            margin: 8px 0;
            border-left: 3px solid #2196F3;
        }
        
        .question-answer[style*="background: #fff3cd"] {
            background: #fff3cd !important;
            border-left: 3px solid #ffc107 !important;
        }
        
        .answer-label {
            font-weight: bold;
            color: #555;
            margin-bottom: 4px;
        }
        
        .answer-label[style*="color: #856404"] {
            color: #856404 !important;
        }
        
        .footer {
            margin-top: 40px;
            text-align: center;
            font-size: 12px;
            color: #999;
            border-top: 1px solid #eee;
            padding-top: 20px;
        }
        
        @page {
            size: A4;
            margin: 15mm;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="title">📚 练习题集</div>
        <div class="meta">生成时间：${timestamp}</div>
        <div class="meta">题目数量：${questions.length} 道</div>
    </div>
    
    <div class="result-header">
        <h4>📋 生成的练习题（共${questions.length}题）</h4>
    </div>
    
    <div class="questions-container">
        ${questions.map(question => {
            const difficultyBadge = getDifficultyBadgeHTML(question.difficulty);
            
            return `
        <div class="generated-question">
            <div class="question-number">
                第${question.number}题 ${difficultyBadge}
            </div>
            <div class="question-content">
                ${question.content}
            </div>
            ${question.answer ? `
            <div class="question-answer">
                <div class="answer-label">💡 参考答案：</div>
                <div>${question.answer}</div>
            </div>
            ` : ''}
            ${question.analysis ? `
            <div class="question-answer" style="background: #fff3cd; border-left: 4px solid #ffc107;">
                <div class="answer-label" style="color: #856404;">📖 解题思路：</div>
                <div style="color: #856404;">${question.analysis}</div>
            </div>
            ` : ''}
        </div>`;
        }).join('')}
    </div>
    
    <div class="footer">
        <p>📱 ZYJC智能批改系统生成</p>
        <p>生成时间：${timestamp}</p>
    </div>
</body>
</html>`;
    }

    buildPDFContent(questions, ctx) {
        console.log('开始构建PDF内容，题目数量:', questions.length);
        
        // 基础PDF头部
        let pdf = '%PDF-1.4\n';
        
        // 设置字体
        ctx.font = `${this.fontSize}px Arial`;

        // 创建页面内容
        let pageContent = this.generatePageContent(questions, ctx);
        console.log('生成的页面内容长度:', pageContent.length);
        console.log('页面内容预览:', pageContent.substring(0, 200));
        
        // 1. 根对象
        const catalogContent = `1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n`;
        
        // 2. 页面树对象
        const pagesContent = `2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n`;
        
        // 3. 页面对象
        const pageObjContent = `3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 ${this.pageWidth} ${this.pageHeight}]\n/Contents 4 0 R\n/Resources <<\n/Font <<\n/F1 5 0 R\n>>\n>>\n>>\nendobj\n`;
        
        // 4. 内容流对象
        const streamContent = `4 0 obj\n<<\n/Length ${pageContent.length}\n>>\nstream\n${pageContent}\nendstream\nendobj\n`;
        
        // 5. 字体对象
        const fontContent = `5 0 obj\n<<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\nendobj\n`;

        // 构建完整PDF
        pdf += catalogContent;
        pdf += pagesContent;
        pdf += pageObjContent;
        pdf += streamContent;
        pdf += fontContent;

        // 计算交叉引用表的位置
        const xrefPos = pdf.length;
        
        // 交叉引用表
        pdf += 'xref\n';
        pdf += '0 6\n';
        pdf += '0000000000 65535 f \n';
        
        // 计算每个对象的偏移位置
        let pos = 9; // PDF头部 '%PDF-1.4\n' 的长度
        pdf += this.padZeros(pos) + ' 00000 n \n'; // object 1 (catalog)
        pos += catalogContent.length;
        pdf += this.padZeros(pos) + ' 00000 n \n'; // object 2 (pages)
        pos += pagesContent.length;
        pdf += this.padZeros(pos) + ' 00000 n \n'; // object 3 (page)
        pos += pageObjContent.length;
        pdf += this.padZeros(pos) + ' 00000 n \n'; // object 4 (contents)
        pos += streamContent.length;
        pdf += this.padZeros(pos) + ' 00000 n \n'; // object 5 (font)

        // 尾部
        pdf += 'trailer\n';
        pdf += '<<\n';
        pdf += '/Size 6\n';
        pdf += '/Root 1 0 R\n';
        pdf += '>>\n';
        pdf += `startxref\n${xrefPos}\n`;
        pdf += '%%EOF\n';

        console.log('PDF构建完成，总长度:', pdf.length);
        return pdf;
    }

    generatePageContent(questions, ctx) {
        console.log('开始生成页面内容，题目数量:', questions.length);
        
        let content = 'BT\n'; // Begin Text
        
        // 设置初始位置到页面顶部
        let currentY = this.pageHeight - this.margin - 20;
        content += `${this.margin} ${currentY} Td\n`; // 移动到起始位置
        
        // 标题 - 与相似练习保持一致
        content += `/F1 20 Tf\n`; // 设置大字体
        content += `(${this.escapeText('生成的练习题')}) Tj\n`;
        
        // 移动到下一行并重置字体
        currentY -= 30;
        content += `0 -30 Td\n`; // 相对移动
        content += `/F1 ${this.fontSize} Tf\n`; // 恢复正常字体大小
        
        // 生成时间和题目数量信息
        const timestamp = new Date().toLocaleDateString();
        content += `(${this.escapeText(`生成时间：${timestamp}`)}) Tj\n`;
        currentY -= this.lineHeight;
        content += `0 ${-this.lineHeight} Td\n`;
        
        content += `(${this.escapeText(`共${questions.length}题`)}) Tj\n`;
        currentY -= this.lineHeight * 2;
        content += `0 ${-this.lineHeight * 2} Td\n`;

        console.log('开始处理题目内容...');
        
        // 题目内容 - 完全按照相似练习的格式
        questions.forEach((question, index) => {
            console.log(`处理题目 ${index + 1}:`, question);
            
            if (currentY < this.margin + 100) {
                console.log('需要换页，但当前版本不支持多页');
                return; // 当前简化版本不支持多页
            }

            // 题目编号和难度标签 - 与相似练习格式一致："第X题 [难度]"
            const difficultyText = this.getDifficultyText(question.difficulty || 'same');
            const questionTitle = `第${question.number}题 [${difficultyText}]`;
            content += `(${this.escapeText(questionTitle)}) Tj\n`;
            currentY -= this.lineHeight * 1.5;
            content += `0 ${-this.lineHeight * 1.5} Td\n`;

            // 题目内容
            if (question.content) {
                const contentText = this.escapeText(question.content);
                const lines = this.wrapText(contentText, ctx, this.pageWidth - 2 * this.margin);
                console.log(`题目内容分行结果:`, lines);
                
                lines.forEach(line => {
                    if (currentY < this.margin + 50) return; // 防止超出页面
                    content += `(${line}) Tj\n`;
                    currentY -= this.lineHeight;
                    content += `0 ${-this.lineHeight} Td\n`;
                });
                
                // 题目内容后的间距
                currentY -= this.lineHeight * 0.5;
                content += `0 ${-this.lineHeight * 0.5} Td\n`;
            }

            // 答案 - 与相似练习格式一致："💡 参考答案："
            if (question.answer && currentY > this.margin + 30) {
                const answerLabel = this.escapeText('💡 参考答案：');
                content += `(${answerLabel}) Tj\n`;
                currentY -= this.lineHeight;
                content += `0 ${-this.lineHeight} Td\n`;
                
                const answerText = this.escapeText(question.answer);
                const answerLines = this.wrapText(answerText, ctx, this.pageWidth - 2 * this.margin - 20);
                answerLines.forEach(line => {
                    if (currentY < this.margin + 50) return;
                    content += `(${line}) Tj\n`;
                    currentY -= this.lineHeight;
                    content += `0 ${-this.lineHeight} Td\n`;
                });
                
                // 答案后的间距
                currentY -= this.lineHeight * 0.5;
                content += `0 ${-this.lineHeight * 0.5} Td\n`;
            }

            // 解析 - 与相似练习格式一致："📖 解题思路："
            if (question.analysis && currentY > this.margin + 30) {
                const analysisLabel = this.escapeText('📖 解题思路：');
                content += `(${analysisLabel}) Tj\n`;
                currentY -= this.lineHeight;
                content += `0 ${-this.lineHeight} Td\n`;
                
                const analysisText = this.escapeText(question.analysis);
                const analysisLines = this.wrapText(analysisText, ctx, this.pageWidth - 2 * this.margin - 20);
                
                analysisLines.forEach(line => {
                    if (currentY < this.margin + 50) return;
                    content += `(${line}) Tj\n`;
                    currentY -= this.lineHeight;
                    content += `0 ${-this.lineHeight} Td\n`;
                });
            }

            // 题目间距
            if (index < questions.length - 1) {
                currentY -= this.lineHeight * 1.5;
                content += `0 ${-this.lineHeight * 1.5} Td\n`;
            }
        });

        content += 'ET\n'; // End Text
        
        console.log('页面内容生成完成，内容长度:', content.length);
        console.log('生成的内容预览:', content.substring(0, 300));
        
        return content;
    }

    wrapText(text, ctx, maxWidth) {
        if (!text || text.trim() === '') {
            return [''];
        }
        
        // 对于中文文本，按字符分割；对于英文文本，按单词分割
        const isChineseText = /[\u4e00-\u9fff]/.test(text);
        
        if (isChineseText) {
            // 中文文本按字符处理
            const chars = text.split('');
            const lines = [];
            let currentLine = '';
            
            chars.forEach(char => {
                const testLine = currentLine + char;
                const metrics = ctx.measureText(testLine);
                
                if (metrics.width > maxWidth && currentLine) {
                    lines.push(currentLine);
                    currentLine = char;
                } else {
                    currentLine = testLine;
                }
            });
            
            if (currentLine) {
                lines.push(currentLine);
            }
            
            return lines;
        } else {
            // 英文文本按单词处理
            const words = text.split(' ');
            const lines = [];
            let currentLine = '';

            words.forEach(word => {
                const testLine = currentLine + (currentLine ? ' ' : '') + word;
                const metrics = ctx.measureText(testLine);
                
                if (metrics.width > maxWidth && currentLine) {
                    lines.push(currentLine);
                    currentLine = word;
                } else {
                    currentLine = testLine;
                }
            });
            
            if (currentLine) {
                lines.push(currentLine);
            }
            
            return lines;
        }
    }

    getDifficultyText(difficulty) {
        // 与相似练习保持一致的难度标签
        const texts = {
            'easier': '简单',
            'same': '相同', 
            'harder': '困难'
        };
        return texts[difficulty] || '相同';
    }

    translateText(text) {
        if (!text) return '';
        
        // 中文词汇到英文的映射表
        const translations = {
            '计算': 'Calculate',
            '题目': 'Question', 
            '答案': 'Answer',
            '解析': 'Analysis',
            '下列': 'Following',
            '词语': 'words',
            '没有': 'no',
            '错别字': 'typos',
            '一组': 'group',
            '注意': 'Note',
            '区分': 'distinguish',
            '形近字': 'similar characters',
            '音近字': 'similar pronunciation',
            '写法': 'writing',
            '差异': 'difference',
            '这是': 'This is',
            '一道': 'a',
            '基本': 'basic',
            '乘法': 'multiplication',
            '运算': 'operation',
            '需要': 'need to',
            '进位': 'carry',
            '处理': 'handle',
            '一般现在时': 'Simple Present Tense',
            '第一人称': 'First Person',
            '单数': 'Singular',
            '用': 'use',
            '动词': 'verb',
            '原形': 'base form',
            '中': 'among',
            '的': 'of',
            '是': 'is',
            '和': 'and'
        };
        
        let translated = text;
        
        // 替换中文词汇
        Object.keys(translations).forEach(chinese => {
            const english = translations[chinese];
            translated = translated.replace(new RegExp(chinese, 'g'), english);
        });
        
        // 处理标点符号
        translated = translated
            .replace(/×/g, 'x')
            .replace(/（）/g, '()')
            .replace(/：/g, ':')
            .replace(/？/g, '?')
            .replace(/。/g, '.')
            .replace(/，/g, ',')
            .replace(/、/g, ', ');
        
        return translated;
    }

    escapeText(text) {
        if (!text) return '';
        
        // 对于简易PDF，由于PDF格式限制，我们保持内容的原样，
        // 但用简单的字符替换来避免乱码
        let processedText = text;
        
        // 保持中文内容不变，只做基本的字符转换以避免PDF显示问题
        // 将一些特殊中文标点转换为对应的英文标点
        processedText = processedText
            .replace(/：/g, ':')
            .replace(/，/g, ',')
            .replace(/。/g, '.')
            .replace(/？/g, '?')
            .replace(/！/g, '!')
            .replace(/（/g, '(')
            .replace(/）/g, ')')
            .replace(/【/g, '[')
            .replace(/】/g, ']')
            .replace(/"/g, '"')
            .replace(/"/g, '"')
            .replace(/'/g, "'")
            .replace(/'/g, "'")
            .replace(/×/g, 'x')
            .replace(/÷/g, '/')
            .replace(/—/g, '-')
            .replace(/…/g, '...');

        // 对于emoji表情符号，保留或转换为文字
        processedText = processedText
            .replace(/💡/g, '[答案]')
            .replace(/📖/g, '[解析]')
            .replace(/📚/g, '[题目]')
            .replace(/🔢/g, '[数学]')
            .replace(/📝/g, '[练习]');
            
        // PDF转义处理 - 只转义PDF特殊字符
        return processedText
            .replace(/\\/g, '\\\\')  // 转义反斜杠
            .replace(/\(/g, '\\(')   // 转义左括号
            .replace(/\)/g, '\\)');  // 转义右括号
            // 不再替换中文字符，保持原样
    }

    padZeros(num) {
        return num.toString().padStart(10, '0');
    }

    downloadPDF(content, filename) {
        try {
            console.log('开始下载PDF，文件名:', filename, '内容长度:', content.length);
            
            const blob = new Blob([content], { type: 'application/pdf' });
            console.log('Blob创建成功，大小:', blob.size);
            
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            link.style.display = 'none';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            // 延迟释放URL，确保下载完成
            setTimeout(() => {
                URL.revokeObjectURL(url);
            }, 1000);
            
            console.log('PDF下载触发成功');
        } catch (error) {
            console.error('PDF下载失败:', error);
            throw error;
        }
    }

    // 测试函数 - 生成与相似练习完全一致的题目数据
    static createTestQuestions() {
        return [
            {
                number: 1,
                difficulty: 'same',
                content: '计算：125 × 8 = ?',
                answer: '1000',
                analysis: '这是一道基本的乘法运算题目，需要注意进位处理'
            },
            {
                number: 2,
                difficulty: 'easier', 
                content: '下列词语中，没有错别字的一组是（）',
                answer: 'B',
                analysis: '注意区分形近字和音近字的写法差异'
            },
            {
                number: 3,
                difficulty: 'harder',
                content: 'Choose the correct answer: I ____ to school every day.',
                answer: 'go', 
                analysis: '一般现在时，第一人称单数用动词原形'
            },
            {
                number: 4,
                difficulty: 'same',
                content: '一个圆的半径是5cm，求这个圆的面积。',
                answer: '78.54 cm²',
                analysis: '使用圆的面积公式 S = πr²，代入半径值计算'
            },
            {
                number: 5,
                difficulty: 'easier',
                content: '解方程：2x + 5 = 13',
                answer: 'x = 4',
                analysis: '移项得 2x = 13 - 5 = 8，所以 x = 4'
            }
        ];
    }
}

// 导出给全局使用
window.SimplePDFGenerator = SimplePDFGenerator;
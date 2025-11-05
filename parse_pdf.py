#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pdfplumber
import sys
import os

def extract_pdf_text(pdf_path):
    """PDF 파일에서 텍스트를 추출합니다."""
    text_content = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"총 페이지 수: {len(pdf.pages)}")
            
            for i, page in enumerate(pdf.pages, 1):
                print(f"페이지 {i} 처리 중...")
                text = page.extract_text()
                if text:
                    text_content.append(f"\n{'='*80}\n페이지 {i}\n{'='*80}\n")
                    text_content.append(text)
                else:
                    text_content.append(f"\n{'='*80}\n페이지 {i} - 텍스트 없음\n{'='*80}\n")
                    
            # 테이블 추출 시도
            tables_found = False
            for i, page in enumerate(pdf.pages, 1):
                tables = page.extract_tables()
                if tables:
                    tables_found = True
                    text_content.append(f"\n{'='*80}\n페이지 {i} - 테이블 데이터\n{'='*80}\n")
                    for table_idx, table in enumerate(tables, 1):
                        text_content.append(f"\n[테이블 {table_idx}]\n")
                        for row in table:
                            if row:
                                text_content.append(" | ".join(str(cell) if cell else "" for cell in row))
                                text_content.append("\n")
                                
    except Exception as e:
        return f"PDF 파싱 오류: {str(e)}"
    
    return "".join(text_content)

if __name__ == "__main__":
    pdf_path = r"doc/패션 Agentic AI 가상 피팅 POC 개발 계획서.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"파일을 찾을 수 없습니다: {pdf_path}")
        sys.exit(1)
    
    print(f"PDF 파일 분석 중: {pdf_path}")
    extracted_text = extract_pdf_text(pdf_path)
    
    # 결과를 파일로 저장
    output_file = "pdf_extracted_text.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(extracted_text)
    
    print(f"\n추출 완료! 결과가 {output_file}에 저장되었습니다.")
    print(f"총 문자 수: {len(extracted_text)}")
    
    # 처음과 끝 부분 일부 출력
    print("\n=== 처음 500자 ===\n")
    print(extracted_text[:500])
    print("\n=== 끝 부분 500자 ===\n")
    print(extracted_text[-500:])


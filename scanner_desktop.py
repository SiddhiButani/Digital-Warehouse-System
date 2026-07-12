import cv2
import sqlite3
import os
import sys

# Setup paths to import from database module
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from database.db import get_db_connection
from models.product import Product

def get_product_details(product_id):
    conn = get_db_connection()
    row = conn.execute(
        """SELECT p.product_name, p.quantity, p.shelf_id, sh.zone AS shelf_zone
           FROM products p 
           LEFT JOIN warehouse_shelves sh ON p.shelf_id = sh.shelf_id
           WHERE p.id = ?;""", 
        (product_id,)
    ).fetchone()
    conn.close()
    return row

def apply_stock_change(product_id, tx_type, qty):
    # Operator is Admin (id=1) for desktop workstation audits
    success, message = Product.adjust_stock(product_id, tx_type, qty, 1)
    return success, message

def main():
    print("====================================================")
    print("   Digital Warehouse - Desktop OpenCV Scan Station   ")
    print("====================================================")
    print("Instructions:")
    print("1. Point webcam to a printed Product QR Code.")
    print("2. The script will highlight the QR code and pause.")
    print("3. Follow terminal prompts to perform Stock operations.")
    print("4. Press 'q' or 'ESC' in the webcam window to exit.")
    print("====================================================")

    # Initialize video capture (0 is default camera)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not open webcam camera feed. Verify connection.")
        return

    # Initialize OpenCV QR Code Detector
    detector = cv2.QRCodeDetector()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame from camera.")
            break

        # Flip horizontally for natural mirror feel
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # Draw a visual scanner target overlay in screen center
        box_size = 250
        x1 = int((w - box_size) / 2)
        y1 = int((h - box_size) / 2)
        x2 = x1 + box_size
        y2 = y1 + box_size
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), (246, 92, 139), 2) # Purple/violet bounding box
        cv2.putText(frame, "Align QR Code inside box", (x1 - 10, y1 - 15), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (246, 92, 139), 2)
        cv2.putText(frame, "Press 'q' to Quit", (15, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Scan for QR code
        data, bbox, _ = detector.detectAndDecode(frame)

        if data:
            # Highlight QR Code with blue boundary box
            if bbox is not None and len(bbox) > 0:
                pts = bbox[0].astype(int)
                for i in range(len(pts)):
                    cv2.line(frame, tuple(pts[i]), tuple(pts[(i+1)%len(pts)]), (212, 182, 6), 3) # Teal/blue green border
            
            # Retrieve Product Details
            product = get_product_details(data)
            
            if product:
                p_name = product['product_name']
                curr_qty = product['quantity']
                shelf = product['shelf_id'] or 'Unassigned'
                
                # Render text overlay on webcam window
                cv2.putText(frame, f"SKU: {data}", (x1, y2 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(frame, f"Name: {p_name}", (x1, y2 + 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(frame, f"Stock: {curr_qty} | Shelf: {shelf}", (x1, y2 + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Show frame with status overlay
                cv2.imshow("DWMS Desktop Scanner", frame)
                cv2.waitKey(100) # Yield a bit to draw

                # Print details and process command in Terminal
                print("\n" + "="*50)
                print(f"[FOUND] Product SKU Detected: {data}")
                print(f"Product: {p_name}")
                print(f"Current Stock: {curr_qty} units")
                print(f"Shelf Location: {shelf} ({product['shelf_zone'] or 'No Zone'})")
                print("="*50)
                
                # Prompt user in terminal
                while True:
                    action = input("Choose Stock Action: [I]n, [O]ut, or [C]ancel / Scan next: ").strip().upper()
                    if action in ['I', 'O', 'C']:
                        break
                    print("Invalid option. Please type I, O, or C.")
                
                if action == 'C':
                    print("[PAUSED] Resuming camera scanning loop...")
                else:
                    tx_type = 'IN' if action == 'I' else 'OUT'
                    action_name = "Receive" if action == 'I' else "Ship"
                    
                    # Ask for quantity
                    while True:
                        try:
                            qty_input = input(f"Enter quantity to {action_name}: ").strip()
                            qty = int(qty_input)
                            if qty > 0:
                                break
                            print("Quantity must be positive.")
                        except ValueError:
                            print("Please enter a valid integer.")
                    
                    # Apply changes
                    success, message = apply_stock_change(data, tx_type, qty)
                    if success:
                        print(f"[SUCCESS] {message}")
                    else:
                        print(f"[ERROR] {message}")
                    
                    print("\nPress any key on terminal to resume scanning...")
                    input()
            else:
                # Scanned data exists but no database product matches it
                cv2.putText(frame, f"SKU {data} NOT FOUND", (x1, y2 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                cv2.imshow("DWMS Desktop Scanner", frame)
                cv2.waitKey(100)
                print(f"\n[ALERT] Scanned QR data '{data}' does not match any registered product.")
                print("Press Enter to continue scanning...")
                input()

        # Render webcam feed
        cv2.imshow("DWMS Desktop Scanner", frame)

        # Break loop on 'q' or 'ESC' key press
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

    # Cleanup resource captures
    cap.release()
    cv2.destroyAllWindows()
    print("\nDesktop Scan Station closed successfully.")

if __name__ == '__main__':
    main()

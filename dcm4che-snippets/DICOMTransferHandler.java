/* ***** BEGIN LICENSE BLOCK *****
 * Version: MPL 1.1/GPL 2.0/LGPL 2.1
 *
 * The contents of this file are subject to the Mozilla Public License Version
 * 1.1 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 * http://www.mozilla.org/MPL/
 *
 * Software distributed under the License is distributed on an "AS IS" basis,
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
 * for the specific language governing rights and limitations under the
 * License.
 *
 * The Original Code is part of dcm4che, an implementation of DICOM(TM) in
 * Java(TM), hosted at https://github.com/gunterze/dcm4che.
 *
 * The Initial Developer of the Original Code is
 * Agfa Healthcare.
 * Portions created by the Initial Developer are Copyright (C) 2011
 * the Initial Developer. All Rights Reserved.
 *
 * Contributor(s):
 * See @authors listed below
 *
 * Alternatively, the contents of this file may be used under the terms of
 * either the GNU General Public License Version 2 or later (the "GPL"), or
 * the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
 * in which case the provisions of the GPL or the LGPL are applicable instead
 * of those above. If you wish to allow use of your version of this file only
 * under the terms of either the GPL or the LGPL, and not to allow others to
 * use your version of this file under the terms of the MPL, indicate your
 * decision by deleting the provisions above and replace them with the notice
 * and other provisions required by the GPL or the LGPL. If you do not delete
 * the provisions above, a recipient may use your version of this file under
 * the terms of any one of the MPL, the GPL or the LGPL.
 *
 * ***** END LICENSE BLOCK ***** */

package org.cardiacatlas.dicom;


import java.io.IOException;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;

import org.dcm4che3.data.Attributes;
import org.dcm4che3.data.Tag;
import org.dcm4che3.net.Association;
import org.dcm4che3.net.DimseRSPHandler;
import org.dcm4che3.net.Status;

/**
 * 
 * A class to handle SCU returned request.
 * 
 * @author Avan Suinesiaputra <avan.sp@gmail.com>
 *
 */
public class DICOMTransferHandler extends DimseRSPHandler {
	
	protected int cancelAfter;        // set how many transfer more before stopping
	protected final AtomicInteger matchCounter = new AtomicInteger();
	
	private Consumer<Attributes> onResult = DICOMTransferHandler::onResultPrint;
	
	public DICOMTransferHandler(Association _as) {
		super(_as.nextMessageID());
	}
	
	public void setOnResult(Consumer<Attributes> f) {
		this.onResult = f;
	}
	
	public void setOnResult(DICOMResultAbstractHook hook) {
		this.onResult = hook::onResult;
	}
	
    @Override
    public void onDimseRSP(Association as, Attributes cmd, Attributes data) {
    	
        super.onDimseRSP(as, cmd, data);
        int status = cmd.getInt(Tag.Status, -1);
        if (Status.isPending(status)) {
            this.onResult.accept(data);
            this.matchCounter.incrementAndGet();
            if (cancelAfter != 0 && this.matchCounter.get() >= cancelAfter)
                try {
                    cancel(as);
                    cancelAfter = 0;
                } catch (IOException e) {
                    e.printStackTrace();
                }
        }
    }
    
    public void setCancelAfter(int _cancelAfter) {
    		this.cancelAfter = _cancelAfter;
    }
	
	private static void onResultPrint(Attributes data) {
		System.out.println(data.toString());
	}
    
}

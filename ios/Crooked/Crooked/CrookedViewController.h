//
//  CrookedViewController.h
//  Crooked
//
//  Created by Aaron Stacy on 11/25/11.
//  Copyright (c) 2011 StoredIQ. All rights reserved.
//

#import <UIKit/UIKit.h>
#import <AVFoundation/AVFoundation.h>
//#import <NSUR

@interface CrookedViewController : UIViewController <AVAudioPlayerDelegate, NSURLConnectionDelegate> {
    AVAudioPlayer* player;
    AVAudioRecorder* recorder;
    
    NSMutableURLRequest* request;
    NSURLConnection* connection;
    
    UIBackgroundTaskIdentifier bgTaskId;
}

@property (weak, nonatomic) IBOutlet UIButton* recordButton;

@property (weak, nonatomic) IBOutlet UIButton* playButton;

@property (weak, nonatomic) IBOutlet UITextField *hostTextField;

//@property (weak, nonatomic) IBOutlet UILabel *outputLabel;
@property (weak, nonatomic) IBOutlet UITextView *outputLabel;

@property (copy, nonatomic) NSURL* url;

@property (strong, nonatomic) NSMutableDictionary* recordSettings;

@property (strong, nonatomic) NSMutableData* data;

- (IBAction)record:(id)sender;

- (void)startRecord;

- (void)stopRecord;

- (IBAction)play:(id)sender;

- (void)startPlay;

- (void)stopPlay;

- (void)audioPlayerDidFinishPlaying:(AVAudioPlayer*)plyr successfully:(BOOL)flag;

- (BOOL) textFieldShouldReturn:(UITextField*)hostTextField;

- (void)connection:(NSURLConnection*)connection didReceiveResponse:(NSURLResponse *)response;

- (void)connection:(NSURLConnection*)connection didReceiveData:(NSData*)data;

- (void)connection:(NSURLConnection*)connection didFailWithError:(NSError*)error;

- (void)connectionDidFinishLoading:(NSURLConnection *)connection;

- (void)toggleBackgroundTask;

@end